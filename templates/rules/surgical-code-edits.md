---
name: surgical-code-edits
description: Change only the minimum needed — no collateral refactors, no unsolicited improvements, no spontaneous docstrings
type: feedback
tags:
  - code-edits
  - discipline
  - minimal-change
---

When you modify a file, change **only the minimum needed** for the requested task. No collateral refactors, no "while I'm at it" cleanups, no spontaneous beautifications, no docstrings or comments added unless explicitly requested.

**Why:** Diffs should be small and easy to review. Surprise refactors make code review harder, can introduce regressions invisible in the main diff, and mix unrelated intents in the same commit. A commit should do ONE thing.

**How to apply:**
- Bug fix? Change only the lines related to the bug. Do NOT reformat surrounding code.
- New feature? Do NOT rename existing variables for "consistency".
- Do NOT add docstrings or comments to existing functions that lack them (unless asked).
- Do NOT extract helper functions "for cleanliness" if they aren't reused immediately.
- See a bug next to your task? **Flag it**, don't fix it in the same commit. Let the user open a separate issue.
- Exception: if a collateral refactor is strictly required for the fix (e.g. a signature change forces caller updates), proceed and flag it explicitly.
