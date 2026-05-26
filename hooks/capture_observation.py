#!/usr/bin/env python3
"""SessionEnd hook implementation — Layer 3 (observation buffer).

Reads {session_id, transcript_path, cwd, end_reason} JSON on stdin and writes
ONE compact Markdown note summarizing the session into the observations store.

Deterministic only: it extracts what the transcript already contains (user
prompts, tools used, files touched). No LLM call — intelligent distillation
stays the job of /pm-checkpoint. The note is plain Markdown indexed by
basic-memory and reachable via /pm-recall; it is never auto-injected.
"""
import json
import os
import re
import sys
import glob
import subprocess
from datetime import datetime

BM = os.environ.get('PM_BASIC_MEMORY_BIN', 'basic-memory')
BM_CONFIG = os.path.expanduser('~/.basic-memory/config.json')
OBS_PROJECT = os.environ.get('PM_OBSERVATIONS_PROJECT', 'persistmind-observations')
OBS_ROOT = os.path.expanduser(
    os.environ.get('PM_OBSERVATIONS_ROOT', '~/.claude/observations')
)

MAX_PROMPTS = 20
PROMPT_MAXLEN = 280
FILE_TOOLS = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}
COMMAND_TAG_RE = re.compile(r'<command-[^>]*>(.*?)</command-[^>]*>', re.DOTALL)
ANY_TAG_RE = re.compile(r'<[^>]+>')


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return

    transcript = (data.get('transcript_path') or '').strip()
    cwd = (data.get('cwd') or '').strip()
    session_id = (data.get('session_id') or '').strip()
    end_reason = (data.get('end_reason') or data.get('reason') or '').strip()
    if not transcript or not os.path.isfile(os.path.expanduser(transcript)):
        return

    prompts, tools, files, first_ts, last_ts = parse_transcript(
        os.path.expanduser(transcript)
    )
    if not prompts:
        return  # nothing worth recording (empty / trivial session)

    slug = encode_slug(cwd) if cwd else 'unknown'
    note = render_note(slug, cwd, session_id, end_reason,
                       prompts, tools, files, first_ts, last_ts)

    date = (first_ts or datetime.now().isoformat())[:10]
    sid = (session_id or 'nosid')[:8]
    out_dir = os.path.join(OBS_ROOT, slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{date}-{sid}.md')
    try:
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(note)
    except Exception:
        return

    ensure_project_registered()


def parse_transcript(path):
    prompts, files = [], []
    tools = {}
    first_ts = last_ts = None
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
    except Exception:
        return prompts, tools, files, first_ts, last_ts

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue

        ts = rec.get('timestamp')
        if ts:
            first_ts = first_ts or ts
            last_ts = ts

        rtype = rec.get('type')
        if rec.get('isSidechain'):
            continue  # subagent internals, not the main session trace

        if rtype == 'user' and not rec.get('isMeta'):
            content = (rec.get('message') or {}).get('content')
            if isinstance(content, str):
                clean = clean_prompt(content)
                if clean:
                    prompts.append(clean[:PROMPT_MAXLEN])
        elif rtype == 'assistant':
            content = (rec.get('message') or {}).get('content')
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict) or block.get('type') != 'tool_use':
                        continue
                    name = block.get('name') or '?'
                    tools[name] = tools.get(name, 0) + 1
                    if name in FILE_TOOLS:
                        fp = (block.get('input') or {}).get('file_path')
                        if fp and fp not in files:
                            files.append(fp)

    return prompts[:MAX_PROMPTS], tools, files, first_ts, last_ts


def clean_prompt(text):
    text = text.strip()
    if not text:
        return ''
    # Slash command invocation: keep a readable marker.
    m = re.search(r'<command-name>(.*?)</command-name>', text, re.DOTALL)
    if m:
        return f'[command] {m.group(1).strip()}'
    # Drop local-command stdout / caveats / other harness-only wrappers.
    if text.startswith('<local-command') or text.startswith('<bash-'):
        return ''
    # Strip any stray tags, collapse whitespace.
    text = ANY_TAG_RE.sub('', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def encode_slug(cwd):
    return re.sub(r'[^a-zA-Z0-9]', '-', os.path.realpath(os.path.expanduser(cwd)))


def render_note(slug, cwd, session_id, end_reason,
                prompts, tools, files, first_ts, last_ts):
    date = (first_ts or '')[:10]
    title = f'Session {date} — {os.path.basename(cwd) or slug}'
    tool_summary = ', '.join(
        f'{n}×{c}' for n, c in sorted(tools.items(), key=lambda kv: -kv[1])
    ) or '—'

    fm = [
        '---',
        f'title: {title}',
        'type: observation',
        f'project: {slug}',
        f'project_path: {cwd}',
        f'date: {date}',
        f'session_id: {session_id}',
        'tags: [observation, session]',
        '---',
        '',
    ]
    body = [
        f'# {title}',
        '',
        f'- **Project:** {cwd}',
        f'- **When:** {first_ts or "?"} → {last_ts or "?"}',
        f'- **End reason:** {end_reason or "?"}',
        f'- **Tools:** {tool_summary}',
        '',
        '## Prompts',
    ]
    for i, p in enumerate(prompts, 1):
        body.append(f'{i}. {p}')
    if files:
        body += ['', '## Files touched']
        body += [f'- {f}' for f in files]
    body.append('')
    return '\n'.join(fm + body)


def ensure_project_registered():
    """Best-effort: register the observations project so it is searchable.

    Files are the source of truth and are written regardless; this only wires
    semantic indexing. Silent on any failure.
    """
    try:
        with open(BM_CONFIG) as f:
            cfg = json.load(f)
        if OBS_PROJECT in cfg.get('projects', {}):
            return
    except Exception:
        pass
    try:
        subprocess.run(
            [BM, 'project', 'add', OBS_PROJECT, OBS_ROOT],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15
        )
    except Exception:
        pass


if __name__ == '__main__':
    main()
