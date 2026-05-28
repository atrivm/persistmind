---
description: Semantic search across all memories (global + every project)
argument-hint: "<natural-language query>"
---

# /pm-recall — Cross-project semantic search

Search across all memories (global + every registered Claude Code project) for the entries most relevant to the query.

**Query:** $ARGUMENTS

## Procedure

Run via Bash the following Python one-shot (handles robust parsing of basic-memory output, which sometimes contains control chars that break jq):

```bash
python3 <<'PY'
import json, os, subprocess

QUERY = """$ARGUMENTS"""
GLOBAL_PROJECT = os.environ.get('PM_GLOBAL_PROJECT', 'persistmind-global')

# Multi-account aware: honors BASIC_MEMORY_CONFIG_DIR when set by wrapper aliases.
bm_dir = os.path.expanduser(os.environ.get('BASIC_MEMORY_CONFIG_DIR') or '~/.basic-memory')
with open(os.path.join(bm_dir, 'config.json')) as f:
    cfg = json.load(f)
projects = [n for n in cfg.get('projects', {}) if n != 'main']

all_hits = []
fails = []
for proj in projects:
    try:
        out = subprocess.check_output(
            ['basic-memory', 'tool', 'search-notes', QUERY, '--project', proj],
            stderr=subprocess.DEVNULL, text=True, timeout=15
        )
        data = json.loads(out)
        for r in data.get('results', []):
            if r.get('score', 0) > 0.5:
                all_hits.append({
                    'scope': 'global' if proj == GLOBAL_PROJECT else proj,
                    'title': r.get('title', ''),
                    'file': r.get('file_path', ''),
                    'score': round(r.get('score', 0), 2),
                    'excerpt': (r.get('matched_chunk') or r.get('content') or '').replace('\n', ' ')[:120]
                })
    except Exception as e:
        fails.append((proj, str(e)[:60]))

all_hits.sort(key=lambda x: -x['score'])
print(f"Total hits: {len(all_hits)} across {len(projects)} projects")
print()
for i, h in enumerate(all_hits[:10], 1):
    print(f"{i:2}. [{h['scope']}] {h['title']} - score {h['score']}")
    print(f"     file: {h['file']}")
    print(f"     {h['excerpt']}")
if fails:
    print(f"\n!! {len(fails)} projects failed: {fails}")
PY
```

Then present the results to the user as a Markdown table:

| Rank | Scope | Slug | Score | Excerpt |
|---|---|---|---|---|

## Suggest follow-up actions when relevant
- "Want me to open the full file?"
- "Worth `/pm-promote <slug>`? This rule is universal but lives only in one project."
- "No match → want me to `/pm-remember-global <topic>` to write it?"

## Constraints
- Maximum 10 hits in the table.
- Minimum score 0.5.
- Do not query the `main` project (basic-memory's default, not used by persistmind).
