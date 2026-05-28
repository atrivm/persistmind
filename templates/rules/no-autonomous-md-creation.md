---
name: no-autonomous-md-creation
description: Never create .md files (README, NOTES, PLAN, ANALYSIS, design.md, etc.) without an explicit request
type: feedback
tags:
  - file-creation
  - documentation
  - discipline
---

Do NOT create `.md` files (README, NOTES, PLAN, ANALYSIS, design.md, etc.) without an explicit request from the user.

**Why:** "Preventive" documentation and scratch files pollute the repo and tend to become stale. The conversation, commit messages, and typed memory fragments (`/pm-remember`, `/pm-checkpoint`) already cover traceability needs.

**How to apply:**
- Bug fix → no `FIX_NOTES.md`.
- New feature → no `FEATURE_PLAN.md` or `IMPLEMENTATION.md`.
- Refactor → no `MIGRATION.md`.
- Analysis / audit → report results in the chat, not in a file, unless the user asks for a file.
- Explicit exception: the user says "write a README", "put it in a file", or "save it as a document".
- Structural exception: typed memory files (`~/.claude/memory/persistmind/*.md`, `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/*/memory/*.md`) created by the `/pm-*` commands.
- If in doubt whether a file is needed, ask — do not create.
