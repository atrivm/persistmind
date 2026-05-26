---
description: Remove a memory (global or project) after confirmation
argument-hint: "<memory-name-to-remove>"
---

# /pm-forget — Memory removal

Remove the memory `$ARGUMENTS`.

## Procedure

1. **Search for the memory** across all layers:
   - `~/.claude/memory/global/` (global)
   - `~/.claude/projects/*/memory/` (all projects)

   Match on filename (without extension) or on the `name:` field in the frontmatter.

2. **If more than one match**, present the list to the user via AskUserQuestion: which one to remove?

3. **If no match**, list available memories with similar names (fuzzy match) and propose a correction.

4. **Confirm removal** by showing:
   - Full path
   - 3-line content preview
   - "Are you sure? Removal is permanent (but the daily backup in `~/.claude/backups/` keeps a copy)."

5. **Execute** if confirmed:
   - Backup first: `cp <file> ~/.claude/backups/forgotten_<timestamp>_<slug>.md`
   - Remove the file: `rm <file>`
   - Remove the line from the MEMORY.md index (global or project).
   - Rebuild the basic-memory index: `basic-memory reindex 2>&1 | tail -5`

6. **Final confirmation** in one line: "Removed: `<path>` (backup at `<backup-path>`)".

## Constraints
- NEVER remove without explicit confirmation.
- Always back up before removal.
- If the memory is linked from others (`[[<slug>]]` inside other memories' content), warn the user about possible dangling references.
