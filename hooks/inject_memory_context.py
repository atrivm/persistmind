#!/usr/bin/env python3
"""UserPromptSubmit hook implementation.

Reads {prompt, cwd, ...} JSON on stdin, prints to stdout:
  1) PINNED memories (frontmatter `always_inject: true`) — always shown
  2) SEMANTIC top-3 from the global project + the current cwd's project
"""
from __future__ import annotations

import json
import os
import re
import sys
import subprocess
import glob
import tempfile
import time
from typing import IO, TypedDict

BM = os.environ.get('PM_BASIC_MEMORY_BIN', 'basic-memory')
# Multi-account aware: CLAUDE_CONFIG_DIR and BASIC_MEMORY_CONFIG_DIR are set by
# wrapper aliases (e.g. `claude-work`) to isolate per-account state. Default to
# `~/.claude` and `~/.basic-memory` when unset.
CLAUDE_DIR = os.path.expanduser(os.environ.get('CLAUDE_CONFIG_DIR') or '~/.claude')
BM_CONFIG_DIR = os.path.expanduser(os.environ.get('BASIC_MEMORY_CONFIG_DIR') or '~/.basic-memory')
BM_CONFIG = os.path.join(BM_CONFIG_DIR, 'config.json')
GLOBAL_PROJECT = os.environ.get('PM_GLOBAL_PROJECT', 'persistmind-global')
OBSERVATIONS_PROJECT = os.environ.get('PM_OBSERVATIONS_PROJECT', 'persistmind-observations')
# Pinned memories are injected with their FULL body: a bare pointer line proved
# to carry no behavioral weight (the model never opens the file). The cap keeps
# an oversized pin from bloating every single prompt.
PIN_BODY_MAX = 3500
# Semantic searches must end this long after the hook starts. Past the hook
# timeout in hooks.json (15 s) Claude Code discards the whole output, pinned
# rules included; a search still running at the deadline (a cold start on a
# loaded machine) only loses its own hits.
SEARCH_DEADLINE_S = 10.0
HOOK_START = time.monotonic()


class SearchHit(TypedDict, total=False):
    """The fields this hook reads from a basic-memory search result."""
    title: str
    file_path: str
    score: float
    matched_chunk: str
    content: str


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return

    prompt = (data.get('prompt') or '').strip()
    cwd = (data.get('cwd') or '').strip()
    if len(prompt) < 8:
        return

    try:
        with open(BM_CONFIG) as f:
            cfg = json.load(f)
    except Exception:
        cfg = {'projects': {}}

    project_slug = resolve_project_slug(cwd, cfg)
    pinned = collect_pinned(cfg)
    semantic = collect_semantic(prompt, project_slug, pinned)

    if not pinned and not semantic:
        return

    print_output(pinned, semantic, project_slug)


def resolve_project_slug(cwd: str, cfg: dict) -> str | None:
    """The project of the nearest directory, from cwd upward, with a registered
    project memory: a session that moved into a subfolder (repo/backend) keeps
    its repo's memories."""
    if not cwd:
        return None
    by_path = {}
    for name, p in cfg.get('projects', {}).items():
        path = p.get('path') or ''
        if path:
            by_path[os.path.realpath(os.path.expanduser(path))] = name
    directory = os.path.realpath(cwd)
    while True:
        encoded = re.sub(r'[^a-zA-Z0-9]', '-', directory)
        target = os.path.realpath(os.path.join(CLAUDE_DIR, 'projects', encoded, 'memory'))
        if target in by_path:
            return by_path[target]
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent


# basic-memory sync may prepend a second permalink-only frontmatter block, so
# strip leading blocks repeatedly until real content starts.
def strip_frontmatter(text: str) -> str:
    while True:
        m = re.match(r'\A\s*---\s*\n.*?\n---\s*\n', text, re.DOTALL)
        if not m:
            return text.strip()
        text = text[m.end():]


def collect_pinned(cfg):
    pinned = []
    seen = set()
    for name, p in cfg.get('projects', {}).items():
        if name in ('main', OBSERVATIONS_PROJECT):
            continue
        base = os.path.realpath(os.path.expanduser(p.get('path') or ''))
        if not base or not os.path.isdir(base):
            continue
        for md in glob.glob(os.path.join(base, '**', '*.md'), recursive=True):
            if os.path.basename(md) == 'MEMORY.md':
                continue
            try:
                with open(md, 'r', encoding='utf-8') as fh:
                    head = fh.read(2000)
                    if not re.search(r'^\s*always_inject:\s*true\s*$', head, re.MULTILINE):
                        continue
                    text = head + fh.read()
            except Exception:
                continue
            rel = os.path.relpath(md, base)
            key = (name, rel)
            if key in seen:
                continue
            seen.add(key)
            m = re.search(r'^name:\s*(.+)$', head, re.MULTILINE)
            title = m.group(1).strip() if m else os.path.basename(md).removesuffix('.md')
            scope = 'global' if name == GLOBAL_PROJECT else name
            body = strip_frontmatter(text)
            if len(body) > PIN_BODY_MAX:
                body = body[:PIN_BODY_MAX] + f'\n…[truncated — read `{rel}` for the rest]'
            pinned.append({'scope': scope, 'title': title, 'file': rel, 'body': body})
    return pinned


def query_projects(projects: list[str], prompt: str) -> list[list[SearchHit]]:
    """Searches all projects in parallel; per project, the hits of a search
    that finished before the deadline, else an empty list. Output goes to temp
    files, so a finished search never waits on a stuck one to be read."""
    deadline = HOOK_START + SEARCH_DEADLINE_S
    runs: list[tuple[subprocess.Popen[bytes] | None, IO[bytes] | None]] = []
    for proj in projects:
        proc, out = None, None
        try:
            out = tempfile.TemporaryFile()
            proc = subprocess.Popen(
                [BM, 'tool', 'search-notes', prompt, '--project', proj],
                stdout=out, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
        runs.append((proc, out))
    while time.monotonic() < deadline and any(
            proc is not None and proc.poll() is None for proc, _ in runs):
        time.sleep(0.05)
    results: list[list[SearchHit]] = []
    for proc, out in runs:
        hits: list[SearchHit] = []
        if proc is not None and proc.poll() is None:
            # Kill without waiting: a process stuck on I/O may take long to
            # die, and waiting would push the hook past its timeout.
            proc.kill()
        elif proc is not None and out is not None and proc.returncode == 0:
            try:
                out.seek(0)
                hits = json.loads(out.read()).get('results', []) or []
            except Exception:
                pass
        if out is not None:
            out.close()
        results.append(hits)
    return results


def collect_semantic(prompt: str, project_slug: str | None, pinned: list[dict]) -> list[dict]:
    semantic = []
    targets = [GLOBAL_PROJECT]
    if project_slug and project_slug != GLOBAL_PROJECT:
        targets.append(project_slug)
    for proj, hits in zip(targets, query_projects(targets, prompt)):
        for r in hits:
            if r.get('score', 0) > 0.5:
                scope = 'global' if proj == GLOBAL_PROJECT else proj
                semantic.append({
                    'scope': scope,
                    'title': r.get('title', ''),
                    'file': r.get('file_path', ''),
                    'score': r.get('score', 0),
                    'excerpt': (r.get('matched_chunk') or r.get('content') or '').replace('\n', ' ')[:200],
                })
    # Dedupe by basename of file path — pinned uses `name:` slug, semantic uses
    # prefixed filename; both share the underlying file path which is stable.
    pinned_files = {(p['scope'], os.path.basename(p['file'])) for p in pinned}
    semantic = [s for s in semantic if (s['scope'], os.path.basename(s['file'])) not in pinned_files]
    semantic.sort(key=lambda x: -x['score'])
    return semantic[:3]


def print_output(pinned, semantic, project_slug):
    lines = ['', '## Auto-injected memories', '']
    if pinned:
        lines.append('### Pinned rules — standing user instructions')
        lines.append('')
        lines.append('The user wrote these rules and pinned them (`always_inject: true`). '
                     'Apply them to this reply as if they were typed in the current '
                     'message — they are instructions, not background context.')
        for p in pinned:
            lines.append('')
            lines.append(f"#### [{p['scope']}] {p['title']} (`{p['file']}`)")
            lines.append('')
            lines.append(p['body'] or f"(empty body — read `{p['file']}`)")
    if semantic:
        lines.append('')
        lines.append('### Possibly relevant memories (background context)')
        lines.append('')
        for s in semantic:
            lines.append(f"- [{s['scope']}] [{s['title']}]({s['file']}) — {s['excerpt']}")
    lines.append('')
    src = f'basic-memory `{GLOBAL_PROJECT}`'
    if project_slug and project_slug != GLOBAL_PROJECT:
        src += f' + `{project_slug}`'
    lines.append(f'_Source: {src}._')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
