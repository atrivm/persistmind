---
name: pm-memory-audit
description: 'When the user wants to review, clean up, deduplicate, or audit the persistent memory system — phrases like "clean up memory", "audit memories", "stale memories", "duplicate memories", "review global memory", "review project memory", "any contradictions?", "check memory". Runs structural checks on the memory store: stale entries (unchanged and unlinked for 6 months), duplicates (same topic in two fragments), orphans (no incoming/outgoing links), conflicts (contradictory rules).'
metadata:
  version: 1.0.0
---

# Memory Audit — Memory system maintenance

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

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
ls ~/.claude/memory/persistmind/ | wc -l
echo "=== Per-project ==="
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
for d in "$CLAUDE_DIR"/projects/*/memory/; do
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
For each stale entry, check whether another memory links to it: `grep -rlF "[[<slug>]]" ~/.claude/memory "$CLAUDE_DIR"/projects/*/memory`. No link + old age → flag.

### 4. Duplicate check

For each memory, search with the key words of its `description`. Another file near the top on the same topic → read both: the same rule or fact is likely a duplicate.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/recall.sh" '<word1>|<word2>|<word3>'
```

### 5. Orphan check

A fragment that no other memory links to with `[[<slug>]]` and that links to none itself:

```bash
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
for f in <path>/*.md; do
  slug=$(grep -m1 '^name:' "$f" | sed 's/^name: *//')
  [ -z "$slug" ] && continue
  others=$(grep -rlF "[[$slug]]" ~/.claude/memory "$CLAUDE_DIR"/projects/*/memory 2>/dev/null | grep -vF "$f")
  [ -z "$others" ] && ! grep -q '\[\[' "$f" && echo "orphan: $f"
done
```

### 6. Conflict check

Look for rules with opposing verbs on the same topic. Example: one memory says "use A", another says "do not use A". Heuristic: keyword overlap > 0.8 + opposite sentiment. Only on `feedback`-type memories.

### 7. Report

Compose a table:

```markdown
## Memory audit — <date>

### Stale (unchanged and unlinked for 6 months)
| Memory | Age | Scope | Suggested action |
|---|---|---|---|
| feedback_old_X | 8 months | global | review or /pm-forget |

### Duplicates (same topic)
| Memory A | Memory B | Why |
|---|---|---|
| ... | ... | same rule on <topic> |

### Orphans
| Memory | No in/out links |

### Potential conflicts
| Memory 1 | Memory 2 | Pattern |
|---|---|---|
```

### 8. Suggested actions

For each issue, propose:
- **Stale**: `/pm-forget <name>` or `edit` to refresh relevance
- **Duplicate**: `/pm-promote <A>` if one is already global, or merge → `edit` one and `/pm-forget` the other
- **Orphan**: add `[[link]]` to/from related memories, or `/pm-forget` if truly isolated
- **Conflict**: manual edit with the user to clarify which one wins

### 9. Execute confirmed actions

Only after explicit confirmation for each action. Never bulk-delete or bulk-merge.

## Constraints

- Backup BEFORE every removal/merge (folder `~/.claude/backups/audit-<date>/`).
- Never run actions back-to-back without confirmation pauses.
- A full audit is long: if the system has >500 memories, propose a sampled audit (top 50 most stale, top 20 suspected duplicates).
