---
description: Initialize persistmind for the current user — language and feedback rules
argument-hint: ""
---

# /pm-init — Persistmind setup wizard

Interactive setup that configures persistmind for the current user. Two steps + apply.

The wizard:
1. Asks language preferences.
2. Lets the user pick which feedback rules to enable from the template catalog.
3. Writes a managed block to `~/.claude/CLAUDE.md`, copies the chosen templates into `~/.claude/memory/persistmind/`, and seeds the index.

## Procedure

### Step 0 — Pre-flight

1. Resolve the plugin install path into an absolute path you will reuse for the rest of the wizard. `${CLAUDE_PLUGIN_ROOT}` is **not** reliably exported to Bash tool calls (known Claude Code limitation, issue #9354), so resolve it defensively:
   ```bash
   PR="${CLAUDE_PLUGIN_ROOT:-}"
   if [ -z "$PR" ] || [ ! -d "$PR/templates/rules" ]; then
     PR=$(find ~/.claude/plugins -type d -path '*/persistmind/*/templates/rules' 2>/dev/null \
          | sed 's#/templates/rules$##' | sort -V | tail -1)
   fi
   echo "PLUGIN_ROOT=$PR"
   [ -n "$PR" ] && [ -d "$PR/templates/rules" ] && echo "catalog-ok" || echo "catalog-missing"
   ```
   If the output is `catalog-missing`, abort with:
   `"Cannot locate the persistmind plugin files. Reinstall the plugin and re-run /pm-init."`

   Note the printed `PLUGIN_ROOT` absolute path and use it verbatim as the plugin root for every template `ls`/`Read` later in this wizard. Bash tool calls do not share shell state, so do not assume the `$PR` variable survives across separate calls — substitute the resolved path.

2. Detect prior state. Run via Bash:
   ```bash
   test -d ~/.claude/memory/persistmind && echo "exists" || echo "new"
   ```
   If `exists`, tell the user the wizard will refresh the configuration (idempotent — see Constraints).

3. Detect whether `~/.claude/CLAUDE.md` already contains a `<!-- PERSISTMIND START -->` ... `<!-- PERSISTMIND END -->` block:
   ```bash
   grep -q '<!-- PERSISTMIND START -->' ~/.claude/CLAUDE.md 2>/dev/null && echo "block-exists" || echo "block-missing"
   ```

### Step 1 — Language

Use `AskUserQuestion`:

- "Default language for Claude responses?" — options: `English`, `Italian`, `Spanish`, `French`, `German`, `Portuguese`. (single-select)

Persistmind keeps code, identifiers and commit messages in English regardless of this choice — that constraint lives in the `code-in-english` rule (offered in Step 2).

### Step 2 — Rule selection

1. List rule templates (`<plugin-root>` = the absolute path resolved in Step 0):
   ```bash
   ls "<plugin-root>/templates/rules/"*.md
   ```

2. For each file, Read it and extract the frontmatter `name` and `description`.

3. Build a multi-select `AskUserQuestion` showing each rule with its description. Recommend enabling all by default (label first option `Enable all (recommended)`).

   Question header suggestion: `Rules`.

4. Map the user's selection to slugs.

### Step 3 — Apply

Run these steps in order. Report progress in one line per phase.

**3a. Create storage:**
```bash
mkdir -p ~/.claude/memory/persistmind/
```

**3b. Copy selected rule templates:**
For each picked slug:
1. Read `<plugin-root>/templates/rules/<slug>.md` (plugin root from Step 0).
2. Write a copy to `~/.claude/memory/persistmind/feedback_<slug>.md`. Set the frontmatter `created` field to today's date (run `date '+%Y-%m-%d'` via Bash).
3. If the destination file already exists, skip the copy and report `skipped: <slug> (already enabled)`.

**3c. Seed the rule index `~/.claude/memory/persistmind/MEMORY.md`:**

If the file does not exist, write this skeleton:
```markdown
# Persistmind — Active rules and memories

Managed by the persistmind plugin. Edit individual files in this directory; this index is updated by `/pm-init`, `/pm-remember`, `/pm-promote`, `/pm-forget`.

## Feedback rules
```

Then append one line per activated rule (skip duplicates):
```
- [<slug>](feedback_<slug>.md) — <description from frontmatter>
```

**3d. Update `~/.claude/CLAUDE.md`:**

Compose the managed block (English):

```
<!-- PERSISTMIND START -->
# Persistmind

## Language
- Default response language: <language from Step 1>
- Code, identifiers, commit messages: English

## Active feedback rules
- [<slug-1>](memory/persistmind/feedback_<slug-1>.md) — <description>
- [<slug-2>](memory/persistmind/feedback_<slug-2>.md) — <description>
- ...

_Managed by persistmind. Do not edit between the markers; re-run `/pm-init` to update._
<!-- PERSISTMIND END -->
```

Then:
- If `block-missing`: append the block to the end of `~/.claude/CLAUDE.md` (create the file if it doesn't exist).
- If `block-exists`: replace the existing block in-place using `Edit`. Match from the `<!-- PERSISTMIND START -->` line to the `<!-- PERSISTMIND END -->` line inclusive.

Never modify content outside the markers.

**3e. Register basic-memory project** (idempotent, best-effort):
```bash
basic-memory project add "${PM_GLOBAL_PROJECT:-persistmind-global}" ~/.claude/memory/persistmind 2>&1 | head -5
```
Interpret the result and pick the project name to use for the status check in 3f:
- Success, or output contains `already exists` → the global layer has its own indexed project. Use `${PM_GLOBAL_PROJECT:-persistmind-global}`.
- Output contains `nested within existing project '<X>'` → another basic-memory project already covers this path. That is fine: the files are still indexed by `<X>`. Skip the dedicated project and use `<X>` for 3f. Report this as "covered by `<X>`", not as a failure.
- `command not found` / not installed → warn, skip 3f, and continue (file-based memory still works; semantic search comes online when `basic-memory` is added later).

**3f. Verify with basic-memory** (best-effort):
```bash
basic-memory status --project "<project resolved in 3e>" 2>&1 | tail -5
```

### Step 4 — Final report

Print to the user:

```
Persistmind initialized.
  Storage:     ~/.claude/memory/persistmind/
  Rules:       N activated, M skipped
  CLAUDE.md:   block <added | updated>
  Sync:        <ok (persistmind-global) | covered by <project> | basic-memory not found>

Next steps:
  /pm-remember "<fact>"       — capture a project fact
  /pm-remember-global "<fact>" — capture a cross-project rule
  /pm-checkpoint              — end-of-session memory review
```

## Constraints

- **Idempotent.** Re-running the wizard replaces the PERSISTMIND block in `CLAUDE.md` in-place, never appends a duplicate, and never overwrites existing rule files unless the user explicitly opts in.
- **No edits outside markers.** Touching `CLAUDE.md` outside `<!-- PERSISTMIND START -->` / `<!-- PERSISTMIND END -->` is forbidden — the user owns that space.
- **English output.** The managed block in `CLAUDE.md` and the `MEMORY.md` skeleton are always in English. Only the chat responses follow the Step 1 language preference.
- **Best-effort sync.** Missing `basic-memory` is not a fatal error — warn but proceed.
