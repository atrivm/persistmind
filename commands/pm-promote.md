---
description: Promote a memory from project to global (User) scope
argument-hint: "<memory-name-to-promote>"
---

# /pm-promote — Promote memory to global

Promote the memory `$ARGUMENTS` from the current project to the global User layer.

## Procedure

1. **Identify the current project.** `pwd` → slug.

2. **Find the memory.** Look for a file in `~/.claude/projects/<slug>/memory/` matching the given name:
   - Exact match on the filename (without extension)
   - Match on the `name:` field in frontmatter
   - Match on the slug inside the filename

   If none: message "Memory '$ARGUMENTS' not found in the current project. Available memories: <list>".

3. **Read the file.** Load its content and parse the frontmatter.

4. **Confirm with the user** by showing:
   - Source: `<project-path>`
   - Destination: `~/.claude/memory/global/<type>_<slug>.md`
   - Content preview (3-5 lines).

   Use AskUserQuestion: "Promote to global?" — options: Yes (move) / Yes (copy, keep in project too) / No (cancel).

5. **Execute the promotion:**
   - **Move**: copy the file to `~/.claude/memory/global/<type>_<slug>.md`, delete the original, update MEMORY.md in both layers.
   - **Copy**: copy the file into global, leave the original, update both indices.

6. **Update the global file's frontmatter** if needed: `tags` may gain `[global, promoted-from-<slug>]`.

7. **Sync** via `basic-memory sync 2>&1 | tail -5`.

8. **Confirm** in one line.

## When to use
- A rule you applied to project X turns out to be useful for Y and Z too → promote it.
- A working pattern that emerged → becomes a global preference.
- A pointer to an external resource that applies to multiple projects.

## When NOT to use
- Architecture decisions specific to one project (e.g. "we picked Postgres") — keep local.
- Facts about a project's code.
- Historical pivots of a project.
