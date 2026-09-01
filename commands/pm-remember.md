---
description: Save a fact/rule/decision in the current project as a typed fragment
argument-hint: "<content to remember> [--type project|decision|pivot|reference|feedback]"
---

# /pm-remember — Project memory capture

Save the following information as a memory fragment in the current project.

**Input:** $ARGUMENTS

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

## Procedure

1. **Identify the current project.** Run `pwd` via Bash, take the path, and slugify it (e.g. `/home/dev/my-project` → `-home-dev-my-project`). The project memory path is `$CLAUDE_DIR/projects/<slug>/memory/`.

2. **Determine the type.** If the user did not specify, infer between:
   - `project` — stable fact about the project (architecture, stack, constraint)
   - `decision` — deliberate choice (what, why, discarded alternatives)
   - `pivot` — change of direction (date, from X to Y, trigger, impact)
   - `reference` — external pointer (URL, path, recurring command)
   - `feedback` — interaction rule for Claude

3. **Generate frontmatter.** kebab-case slug from the content. Frontmatter:
```yaml
---
name: <kebab-slug>
description: <one line, specific>
metadata:
  type: <type>
  created: <YYYY-MM-DD from `date '+%Y-%m-%d'`>
  tags: [<2-4 relevant tags>]
---
```

4. **Generate the body** based on type:
   - `feedback`/`project`: the rule/fact, then `**Why:**`, then `**How to apply:**`.
   - `decision`: what | why | discarded alternatives | reversible?
   - `pivot`: date | from X to Y | trigger | impact.
   - `reference`: what it is | URL/path | when to consult it.

5. **Write the file** to `$CLAUDE_DIR/projects/<slug>/memory/<type>_<slug>.md` via the Write tool. Create the directory if it does not exist.

6. **Update the index** `$CLAUDE_DIR/projects/<slug>/memory/MEMORY.md`: add a line in the appropriate section with `- [<slug>](<type>_<slug>.md) — <description>`.

7. **Auto-register the project in basic-memory** (idempotent, best-effort). Needed so `/pm-recall` and semantic injection can see this project's memories. Run via Bash:
   ```bash
   PROJECT_NAME=$(echo "<slug>" | sed 's/^-//' | tr '[:upper:]' '[:lower:]')
   basic-memory project add "$PROJECT_NAME" "<CLAUDE_DIR>/projects/<slug>/memory" 2>&1 | head -3 || true
   basic-memory reindex --project "$PROJECT_NAME" 2>&1 | tail -2 || true
   ```
   Substitute `<slug>` with the slug from step 1 and `<CLAUDE_DIR>` with the resolved active config dir. `already exists` and `nested within existing project '<X>'` are both non-fatal. Do NOT rely on the background watcher: `basic-memory mcp` processes only watch projects that existed when they started, so a project registered afterwards is never indexed until a reindex — files stay pending and semantic search silently returns nothing. The reindex call is incremental and idempotent (near-instant when there is nothing new). Confirm with `basic-memory status --project "$PROJECT_NAME" 2>&1 | tail -5`: it must show `No changes`.

8. **Confirm to the user** in one line: "Memory saved: `<path>` (type: <type>, slug: <slug>)".

## Constraints
- Do NOT overwrite existing files without confirmation.
- If you find a similar memory (same slug or close description), suggest editing the existing one instead of creating a new one.
- Never save credentials, tokens, passwords (refuse explicitly).
