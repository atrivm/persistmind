---
name: memory-audit
description: When the user wants to review, clean up, deduplicate, or audit the persistent memory system — phrases like "clean up memory", "audit memories", "stale memories", "duplicate memories", "review global memory", "review project memory", "any contradictions?", "check memory". Runs structural checks on the memory store: stale entries (no recall in 6 months), duplicates (cosine similarity > 0.92), orphans (no incoming/outgoing links), conflicts (contradictory rules).
metadata:
  version: 1.0.0
---

# Memory Audit — Memory system maintenance

Periodic audit of global and per-project memories.

## Procedure

### 1. Pick scope

Ask the user:
- Global only (`~/.claude/memory/`)?
- Current project only?
- All (global + every project)?

### 2. Inventory

```bash
echo "=== Global ==="
ls ~/.claude/memory/global/ | wc -l
echo "=== Per-project ==="
for d in ~/.claude/projects/*/memory/; do
  count=$(ls "$d" 2>/dev/null | grep -v MEMORY.md | wc -l)
  proj=$(basename $(dirname "$d"))
  [ "$count" -gt 0 ] && echo "  $proj: $count"
done
```

### 3. Stale check

Memories with `metadata.created` > 180 days ago, never updated. Pseudo-code:
```bash
find <path> -name "*.md" -mtime +180 -print
```
For each stale entry, check with basic-memory whether it has ever been recalled. Zero hits + old age → flag.

### 4. Duplicate check

For each memory, run a semantic query using its `description` as input. If the top match other than itself has score > 0.92, it's likely a duplicate.

```bash
basic-memory tool search-notes "<description>" --limit 3
```

### 5. Orphan check (basic-memory native)

```bash
basic-memory orphans
```

### 6. Conflict check

Look for rules with opposing verbs on the same topic. Example: one memory says "use A", another says "do not use A". Heuristic: keyword overlap > 0.8 + opposite sentiment. Only on `feedback`-type memories.

### 7. Report

Compose a table:

```markdown
## Memory audit — <date>

### Stale (no recall in 6 months)
| Memory | Age | Scope | Suggested action |
|---|---|---|---|
| feedback_old_X | 8 months | global | review or /forget |

### Duplicates (cosine > 0.92)
| Memory A | Memory B | Score |
|---|---|---|
| ... | ... | 0.94 |

### Orphans
| Memory | No in/out links |

### Potential conflicts
| Memory 1 | Memory 2 | Pattern |
|---|---|---|
```

### 8. Suggested actions

For each issue, propose:
- **Stale**: `/forget <name>` or `edit` to refresh relevance
- **Duplicate**: `/promote <A>` if one is already global, or merge → `edit` one and `/forget` the other
- **Orphan**: add `[[link]]` to/from related memories, or `/forget` if truly isolated
- **Conflict**: manual edit with the user to clarify which one wins

### 9. Execute confirmed actions

Only after explicit confirmation for each action. Never bulk-delete or bulk-merge.

## Constraints

- Backup BEFORE every removal/merge (folder `~/.claude/backups/audit-<date>/`).
- Never run actions back-to-back without confirmation pauses.
- A full audit is long: if the system has >500 memories, propose a sampled audit (top 50 most stale, top 20 suspected duplicates).
