---
description: Analyze the current session and propose what to save to memory before /clear
argument-hint: "(optional) focus area, e.g. 'architectural decisions'"
---

# /checkpoint — End-of-session consolidation

Analyze the entire current conversation and propose a list of memories to save BEFORE `/clear` is run.

**Optional focus area:** $ARGUMENTS

## Procedure

1. **Scan the conversation.** Mentally re-read the whole current session and extract:
   - **Decisions made** (explicit or implicit) — with rationale and discarded alternatives.
   - **Facts discovered** about the project (architecture, constraints, stack, dependencies).
   - **Pivots / direction changes** (we were on A, switched to B because C).
   - **Rules that surfaced** which could become feedback (e.g. the user corrected a behavior).
   - **External pointers** mentioned (URLs, paths, undocumented commands).
   - **Errors / incidents** and the root causes that emerged.

2. **Categorize by scope.**
   For each item, decide: is it specific to this project, or universal?
   - Universal → global
   - Specific → project
   - In doubt → project (you can always `/promote` it later)

3. **Categorize by type.** project | decision | pivot | feedback | reference.

4. **Present the list to the user** as a table or bullet list, with:
   - Proposed slug
   - Type
   - Scope (project/global)
   - 1-line summary
   - 1-line why

5. **Ask for confirmation with AskUserQuestion** (multiSelect) — the user selects which to save. Include "all" and "none" options.

6. **For each confirmed item**, apply the `/remember` or `/remember-global` procedure as appropriate. Do NOT invoke the slash commands — instead, use Write directly on the filesystem + update the index + `basic-memory sync`.

7. **Final report.** One line per file written.

## Constraints
- If the conversation is very long (>50 turns), propose at most 10 memories. Prefer decisions and rules over minor facts.
- No silent capture: every save passes through user confirmation.
- Never capture credentials, tokens, sensitive personal data.
- If the session was purely exploratory (no decisions, no facts), say so: "Nothing significant to save."
