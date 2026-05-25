---
description: Cerca semanticamente in tutte le memorie (globali + tutti i progetti)
argument-hint: "<query in linguaggio naturale>"
---

# /recall — Ricerca semantica cross-project

Cerca nelle memorie (globali + tutti i progetti Claude Code registrati) le entry più rilevanti per la query.

**Query:** $ARGUMENTS

## Procedura

Esegui via Bash il seguente Python one-shot (gestisce parsing robusto dell'output di basic-memory, che a volte contiene control chars che spaccano jq):

```bash
python3 <<'PY'
import json, os, subprocess

QUERY = """$ARGUMENTS"""
GLOBAL_PROJECT = os.environ.get('PM_GLOBAL_PROJECT', 'persistmind-global')

with open(os.path.expanduser('~/.basic-memory/config.json')) as f:
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
print(f"Hit totali: {len(all_hits)} su {len(projects)} project")
print()
for i, h in enumerate(all_hits[:10], 1):
    print(f"{i:2}. [{h['scope']}] {h['title']} — score {h['score']}")
    print(f"     file: {h['file']}")
    print(f"     {h['excerpt']}")
if fails:
    print(f"\n!! {len(fails)} project failed: {fails}")
PY
```

Poi presenta i risultati all'utente in tabella Markdown:

| Rank | Scope | Slug | Score | Estratto |
|---|---|---|---|---|

## Suggerisci azioni se opportuno
- "Vuoi leggere il file completo? Posso aprirlo."
- "Vuoi `/promote <slug>` se questo è universale ma è solo in un progetto?"
- "Nessun match → vuoi `/remember-global <topic>` per scriverlo?"

## Vincoli
- Massimo 10 hit nella tabella.
- Score minimo 0.5.
- Non interrogare il progetto `main` (default basic-memory non usato da persistmind).
