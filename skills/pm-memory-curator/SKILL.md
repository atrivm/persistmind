---
name: pm-memory-curator
description: When the user wants to write a memory (any of /pm-remember, /pm-remember-global, or just dictates "remember that..."), reshape it into the typed-fragment format with frontmatter (name, description, type, tags) and Why/How-to-apply body. Also use when reviewing/editing existing memory files in ~/.claude/memory/ or ${CLAUDE_CONFIG_DIR:-~/.claude}/projects/*/memory/. Ensures memories follow the Memory Contract defined in ~/.claude/CLAUDE.md.
metadata:
  version: 1.0.0
---

# Memory Curator — Writing well-structured memories

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

Help the user turn a free-form observation into a well-formed memory fragment, compliant with the Memory Contract.

## Procedure

1. **Input.** A sentence or paragraph the user wants to remember.

2. **Identify the type** among: `user`, `feedback`, `project`, `decision`, `pivot`, `reference`.

3. **Generate the slug.**
   - kebab-case
   - 2-5 meaningful words
   - No filler articles/prepositions
   - Unique vs. existing memories (check with `basic-memory tool search-notes "<slug>"`)

4. **Write the `description`.**
   - One line, max 100 characters
   - Specific, not generic ("Never bump version without request" yes; "Git rule" no)
   - Match the user's working language (defaults to English)

5. **Pick the tags.**
   - 2-4 tags
   - Common categories: `git`, `ci-cd`, `releases`, `security`, `workflow`, `autonomy`, `debugging`, `ui`, `tooling`, `cost`, `flutter`, `react`, `python`
   - Add `cross-project` if the rule is promotable to global

6. **Generate the body by type.**

   **feedback/project:**
   ```markdown
   <The rule/fact in 1-2 sentences>

   **Why:** <Rationale, ideally referencing an incident or pattern that emerged>

   **How to apply:** <When and how to apply the rule operationally>
   ```

   **decision:**
   ```markdown
   **What:** <Decision made>
   **Why:** <Rationale, data, constraints>
   **Discarded alternatives:** <Which ones and why not>
   **Reversible?:** <Yes/No, with what effort>
   ```

   **pivot:**
   ```markdown
   **Date:** <YYYY-MM-DD>
   **From:** <Previous state>
   **To:** <New state>
   **Trigger:** <What caused it>
   **Impact:** <What changes going forward>
   ```

   **reference:**
   ```markdown
   **What it is:** <Short description>
   **Where:** <URL/path/command>
   **When to consult:** <Use cases>
   ```

7. **Compose the full file:**
   ```yaml
   ---
   name: <slug>
   description: <description>
   metadata:
     type: <type>
     created: <YYYY-MM-DD>
     tags: [<tag1>, <tag2>, ...]
   ---

   <body>
   ```

8. **Show the fragment to the user** BEFORE saving. Ask for confirmation.

9. **Save.** Path:
   - `~/.claude/memory/persistmind/<type>_<slug>.md` for global
   - `$CLAUDE_DIR/projects/<project-slug>/memory/<type>_<slug>.md` for project (active account)

10. **Update the corresponding MEMORY.md index.**

11. **Verify basic-memory pickup** via `basic-memory status 2>&1 | tail -5`.

## Constraints

- Never invent incidents or rationales — ask the user if not specified.
- Never save credentials/tokens/sensitive data.
- If the content is ambiguous between 2 types (e.g. decision vs project), ask the user.
- If a memory with a similar slug already exists, propose an edit instead of a new file.
