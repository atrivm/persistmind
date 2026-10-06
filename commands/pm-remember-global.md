---
description: Save a rule/preference to the global User layer (applies to all projects)
argument-hint: "<content to remember globally> [--type feedback|reference|user]"
---

# /pm-remember-global — Global (User) memory capture

Save the following information as a GLOBAL memory fragment — visible across all projects.

**Input:** $ARGUMENTS

## When to use /pm-remember-global vs /pm-remember
- Global: universal interaction rule, personal preference, cross-project pointer, identity.
- Project: fact/decision/pivot specific to a single project.

If in doubt: PROJECT. You can always `/pm-promote` later when it becomes clear it applies everywhere.

## Procedure

1. **Determine the type.** If not specified:
   - `feedback` — interaction rule Claude must follow
   - `reference` — cross-project pointer (URL, path, command)
   - `user` — fact about the user (who they are, what they prefer, what they know)

2. **Generate frontmatter.** kebab-case slug. Frontmatter:
```yaml
---
name: <kebab-slug>
description: "<one line, specific>"
metadata:
  type: <type>
  created: <YYYY-MM-DD>
  tags: [<2-4 tags>]
---
```
Always write the description between double quotes, escaping any `"` inside it as `\"`: unquoted, a `: ` in it makes the YAML invalid (basic-memory then ignores the whole frontmatter) and a ` #` cuts it short.

3. **Generate the body:**
   - `feedback`: the rule, **Why:**, **How to apply:**.
   - `reference`: what it is, URL/path, when to consult it.
   - `user`: the fact, context, any implications for responses.

4. **Write the file** to `~/.claude/memory/persistmind/<type>_<slug>.md` via the Write tool.

5. **Update the index** `~/.claude/memory/persistmind/MEMORY.md` — add a line in the appropriate section:
   - Identity → `## Identity`
   - Feedback → `## Feedback (cross-project rules — distilled from projects)`
   - Reference → `## Reference`

6. **Index and verify.** Run via Bash: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/reindex_memory.py" --path ~/.claude/memory/persistmind`. basic-memory does not watch files; the script reindexes the basic-memory project that covers the global layer (after any reindex already running) and prints its status, which must show `No changes`. If the script path does not exist, run `basic-memory reindex --project "${PM_GLOBAL_PROJECT:-persistmind-global}"` and `basic-memory status --project "${PM_GLOBAL_PROJECT:-persistmind-global}"` instead.

7. **Confirm** in one line: "GLOBAL memory saved: `~/.claude/memory/persistmind/<file>` (type: <type>)".

## Constraints
- Do not duplicate. First search with `basic-memory tool search-notes "<topic>"` to check if a similar memory exists.
- Global memories are ALWAYS in context: keep them short and actionable, no prose.
- Never save credentials.
