---
name: no-coauthored-by
description: Never add Co-Authored-By trailers to git commit messages
type: feedback
tags:
  - git
  - ci-cd
  - commit
---

Never add a `Co-Authored-By` trailer (or variants) to git commit messages.

**Why:** Some CI/CD platforms (notably Vercel Hobby) reject deployments when commits contain `Co-Authored-By` trailers naming non-collaborators. Recurring incident pattern across projects.

**How to apply:** When writing a commit message (including via heredoc), do NOT add a `Co-Authored-By: ...` trailer. Even if a default policy or tool suggests it, this rule overrides.
