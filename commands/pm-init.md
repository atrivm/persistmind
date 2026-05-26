---
description: Initialize persistmind for the current user — identity, language, and feedback rules
argument-hint: ""
---

# /pm-init — Persistmind setup wizard

Interactive setup that configures persistmind for the current user. Three steps + apply.

The wizard:
1. Asks identity (role, tech stack, optional display name).
2. Asks language preferences.
3. Lets the user pick which feedback rules to enable from the template catalog.
4. Writes a managed block to `~/.claude/CLAUDE.md`, copies the chosen templates into `~/.claude/memory/persistmind/`, and seeds the index.

## Procedure

### Step 0 — Pre-flight

1. Resolve the plugin install path. Use the `${CLAUDE_PLUGIN_ROOT}` environment variable (exposed by Claude Code when running a plugin command). If the variable is not set, abort with:
   `"Cannot resolve CLAUDE_PLUGIN_ROOT. Re-run /pm-init from inside a Claude Code session with the plugin installed."`

2. Verify the template catalog exists:
   ```bash
   ls "$CLAUDE_PLUGIN_ROOT/templates/rules/"*.md 2>/dev/null | head -1
   ```
   If empty, abort with:
   `"Template catalog missing at $CLAUDE_PLUGIN_ROOT/templates/rules/. Reinstall the plugin."`

3. Detect prior state. Run via Bash:
   ```bash
   test -d ~/.claude/memory/persistmind && echo "exists" || echo "new"
   ```
   If `exists`, tell the user the wizard will refresh the configuration (idempotent — see Constraints).

4. Detect whether `~/.claude/CLAUDE.md` already contains a `<!-- PERSISTMIND START -->` ... `<!-- PERSISTMIND END -->` block:
   ```bash
   grep -q '<!-- PERSISTMIND START -->' ~/.claude/CLAUDE.md 2>/dev/null && echo "block-exists" || echo "block-missing"
   ```

### Step 1 — Identity

Use `AskUserQuestion` to gather identity. Single question with three sub-questions where multi-select is appropriate.

- "Primary role?" — options: `Backend engineer`, `Frontend engineer`, `Fullstack engineer`, `Mobile engineer`, `Data engineer / scientist`, `DevOps / SRE`, `Designer`. (single-select)
- "Main tech stack?" — options: `TypeScript / JavaScript`, `Python`, `Go`, `Rust`, `Java / Kotlin`, `Swift`, `Flutter / Dart`, `React / Next.js`, `Vue / Nuxt`, `Svelte / SvelteKit`. (multi-select, 1-4 answers)
- "Display name (optional)?" — present 1-2 plausible default options (e.g. shell `whoami`) plus `Other` for free-text. (single-select)

Save the answers locally for Step 4. Skip silently if the user picks `Other` with empty input on the optional name.

### Step 2 — Language

Use `AskUserQuestion`:

- "Default language for Claude responses?" — options: `English`, `Italian`, `Spanish`, `French`, `German`, `Portuguese`. (single-select)

Persistmind keeps code, identifiers and commit messages in English regardless of this choice — that constraint lives in the `code-in-english` rule (offered in Step 3).

### Step 3 — Rule selection

1. List rule templates:
   ```bash
   ls "$CLAUDE_PLUGIN_ROOT/templates/rules/"*.md
   ```

2. For each file, Read it and extract the frontmatter `name` and `description`.

3. Build a multi-select `AskUserQuestion` showing each rule with its description. Recommend enabling all by default (label first option `Enable all (recommended)`).

   Question header suggestion: `Rules`.

4. Map the user's selection to slugs.

### Step 4 — Apply

Run these steps in order. Report progress in one line per phase.

**4a. Create storage:**
```bash
mkdir -p ~/.claude/memory/persistmind/
```

**4b. Copy selected rule templates:**
For each picked slug:
1. Read `$CLAUDE_PLUGIN_ROOT/templates/rules/<slug>.md`.
2. Write a copy to `~/.claude/memory/persistmind/feedback_<slug>.md`. Set the frontmatter `created` field to today's date (run `date '+%Y-%m-%d'` via Bash).
3. If the destination file already exists, skip the copy and report `skipped: <slug> (already enabled)`.

**4c. Seed the rule index `~/.claude/memory/persistmind/MEMORY.md`:**

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

**4d. Update `~/.claude/CLAUDE.md`:**

Compose the managed block (English):

```
<!-- PERSISTMIND START -->
# Persistmind

## Identity
- Role: <role from Step 1>
- Stack: <comma-separated stack>
- Name: <name if provided, otherwise omit this line>

## Language
- Default response language: <language from Step 2>
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

**4e. Sync basic-memory** (best-effort):
```bash
basic-memory sync 2>&1 | tail -5
```

If `basic-memory` is not installed, report a warning but do not abort — the file-based memory still works; semantic search comes online when `basic-memory` is added later.

### Step 5 — Final report

Print to the user:

```
Persistmind initialized.
  Storage:     ~/.claude/memory/persistmind/
  Rules:       N activated, M skipped
  CLAUDE.md:   block <added | updated>
  Sync:        <ok | basic-memory not found>

Next steps:
  /pm-remember "<fact>"       — capture a project fact
  /pm-remember-global "<fact>" — capture a cross-project rule
  /pm-checkpoint              — end-of-session memory review
```

## Constraints

- **Idempotent.** Re-running the wizard replaces the PERSISTMIND block in `CLAUDE.md` in-place, never appends a duplicate, and never overwrites existing rule files unless the user explicitly opts in.
- **No edits outside markers.** Touching `CLAUDE.md` outside `<!-- PERSISTMIND START -->` / `<!-- PERSISTMIND END -->` is forbidden — the user owns that space.
- **No secrets in Identity.** If the user enters a credential/token in the optional name field, refuse and re-ask.
- **English output.** The managed block in `CLAUDE.md` and the `MEMORY.md` skeleton are always in English. Only the chat responses follow the Step 2 language preference.
- **Best-effort sync.** Missing `basic-memory` is not a fatal error — warn but proceed.
