---
name: memory-audit
description: When the user wants to review, clean up, deduplicate, or audit the persistent memory system — phrases like "pulisci la memoria", "audit memorie", "memorie stale", "memorie duplicate", "rivedi memoria globale", "rivedi memoria del progetto", "ci sono contraddizioni?", "controlla la memoria". Runs structural checks on the memory store: stale entries (no recall in 6 months), duplicates (cosine similarity > 0.92), orphans (no incoming/outgoing links), conflicts (contradictory rules).
metadata:
  version: 1.0.0
---

# Memory Audit — Manutenzione del sistema di memoria

Audit periodico delle memorie globali e per-progetto.

## Procedura

### 1. Scelta scope

Chiedi all'utente:
- Solo globale (`~/.claude/memory/`)?
- Solo progetto corrente?
- Tutto (globale + tutti i progetti)?

### 2. Inventario

```bash
echo "=== Globale ==="
ls ~/.claude/memory/global/ | wc -l
echo "=== Per-progetto ==="
for d in ~/.claude/projects/*/memory/; do
  count=$(ls "$d" 2>/dev/null | grep -v MEMORY.md | wc -l)
  proj=$(basename $(dirname "$d"))
  [ "$count" -gt 0 ] && echo "  $proj: $count"
done
```

### 3. Stale check

Memorie con `metadata.created` > 180 giorni fa, mai aggiornate. Pseudo-code:
```bash
find <path> -name "*.md" -mtime +180 -print
```
Per ogni stale, verifica con basic-memory se ha mai avuto hit di recall. Se 0 hit + età alta → flag.

### 4. Duplicate check

Per ogni memoria, query semantica con il suo `description` come input. Se top match diverso da sé stesso ha score > 0.92, è probabile duplicato.

```bash
basic-memory tool search-notes "<description>" --limit 3
```

### 5. Orphan check (basic-memory native)

```bash
basic-memory orphans
```

### 6. Conflict check

Cerca regole con verb opposti su stesso topic. Esempio: una memoria dice "usa A", un'altra "non usare A". Heuristic: keyword overlap > 0.8 + sentiment inverso. Lo fai solo su memorie tipo `feedback`.

### 7. Report

Componi tabella:

```markdown
## Audit memoria — <data>

### Stale (no recall in 6 mesi)
| Memoria | Età | Scope | Azione suggerita |
|---|---|---|---|
| feedback_old_X | 8 mesi | globale | review o /forget |

### Duplicati (cosine > 0.92)
| Memoria A | Memoria B | Score |
|---|---|---|
| ... | ... | 0.94 |

### Orfani
| Memoria | Nessun link in/out |

### Conflitti potenziali
| Memoria 1 | Memoria 2 | Pattern |
|---|---|---|
```

### 8. Proposte di azione

Per ogni problema, proponi:
- **Stale**: `/forget <name>` o `edit` per rinnovare la rilevanza
- **Duplicate**: `/promote <A>` se uno è già globale, oppure merge → `edit` su una e `/forget` sull'altra
- **Orphan**: aggiungi `[[link]]` da/verso memorie correlate, oppure `/forget` se davvero isolata
- **Conflict**: edit manuale con l'utente per chiarire quale prevale

### 9. Esegui le azioni confermate

Solo dopo conferma esplicita di ogni azione. Mai bulk-delete o bulk-merge.

## Vincoli

- Backup PRIMA di ogni rimozione/merge (cartella `~/.claude/backups/audit-<date>/`).
- Mai eseguire azioni in serie senza pause di conferma.
- Audit completo è lungo: se il sistema ha >500 memorie, propone audit per campione (top 50 più stale, top 20 duplicati sospetti).
