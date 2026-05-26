---
name: search-before-asking
description: Exhaust codebase investigation before asking the user — answers derivable from the repo should not become questions
type: feedback
tags:
  - workflow
  - autonomy
---

Never ask the user a question whose answer is derivable from the codebase, git history, configuration files, or project documentation.

**Why:** Lazy questions break the user's flow and waste time. Mature agents are expected to investigate before asking.

**How to apply:**
1. Before asking, do at least one grep plus one read of the most likely file.
2. If the information remains ambiguous after investigation, THEN ask — but state what you have already verified.
3. Exceptions: design choices, personal preferences, or decisions that genuinely require human judgment.
