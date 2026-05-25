#!/usr/bin/env python3
"""UserPromptSubmit hook implementation.

Reads {prompt, cwd, ...} JSON on stdin, prints to stdout:
  1) PINNED memories (frontmatter `always_inject: true`) — always shown
  2) SEMANTIC top-3 from the global project + the current cwd's project
"""
import json
import os
import re
import sys
import subprocess
import glob

BM = os.environ.get('PM_BASIC_MEMORY_BIN', 'basic-memory')
BM_CONFIG = os.path.expanduser('~/.basic-memory/config.json')
GLOBAL_PROJECT = os.environ.get('PM_GLOBAL_PROJECT', 'persistmind-global')


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


def resolve_project_slug(cwd, cfg):
    if not cwd:
        return None
    encoded = re.sub(r'[^a-zA-Z0-9]', '-', os.path.realpath(cwd))
    target = os.path.realpath(os.path.expanduser(f'~/.claude/projects/{encoded}/memory'))
    for name, p in cfg.get('projects', {}).items():
        path = p.get('path') or ''
        if path and os.path.realpath(os.path.expanduser(path)) == target:
            return name
    return None


def collect_pinned(cfg):
    pinned = []
    seen = set()
    for name, p in cfg.get('projects', {}).items():
        if name == 'main':
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
            except Exception:
                continue
            if not re.search(r'^\s*always_inject:\s*true\s*$', head, re.MULTILINE):
                continue
            rel = os.path.relpath(md, base)
            key = (name, rel)
            if key in seen:
                continue
            seen.add(key)
            m = re.search(r'^name:\s*(.+)$', head, re.MULTILINE)
            title = m.group(1).strip() if m else os.path.basename(md).removesuffix('.md')
            scope = 'global' if name == GLOBAL_PROJECT else name
            pinned.append({'scope': scope, 'title': title, 'file': rel})
    return pinned


def query_project(proj, prompt):
    try:
        out = subprocess.check_output(
            [BM, 'tool', 'search-notes', prompt, '--project', proj],
            stderr=subprocess.DEVNULL, text=True, timeout=10
        )
        return json.loads(out).get('results', []) or []
    except Exception:
        return []


def collect_semantic(prompt, project_slug, pinned):
    semantic = []
    targets = [GLOBAL_PROJECT]
    if project_slug and project_slug != GLOBAL_PROJECT:
        targets.append(project_slug)
    for proj in targets:
        for r in query_project(proj, prompt):
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
    lines = ['', '## Memorie auto-iniettate', '']
    for p in pinned:
        lines.append(f"- [PIN/{p['scope']}] [{p['title']}]({p['file']}) — always-injected (leggi il file per dettagli)")
    for s in semantic:
        lines.append(f"- [{s['scope']}] [{s['title']}]({s['file']}) — {s['excerpt']}")
    lines.append('')
    src = f'basic-memory `{GLOBAL_PROJECT}`'
    if project_slug and project_slug != GLOBAL_PROJECT:
        src += f' + `{project_slug}`'
    lines.append(f"_Source: {src}. PIN = sempre iniettate (`always_inject: true`)._")
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
