---
name: investigation-rigor
description: Verify diagnoses with at least one concrete observation before asserting — no rushed conclusions
type: feedback
tags:
  - debugging
  - workflow
  - honesty
---

Before declaring "I understand the problem" or "the cause is X", verify with at least one concrete observation: a log line, a grep, a test, or a read of the relevant file. If you notice a rushed conclusion, admit it explicitly and reopen the analysis.

**Why:** Rushing to a conclusion is more expensive than the rigor of verifying. Misdiagnosed bugs translate to real production incidents and wasted hours of follow-up work.

**How to apply:**
- Diagnose → verify → confirm → fix. In this order.
- Never say "it should be X, let me try the fix". First confirm it IS X.
- If mid-investigation you realize your diagnosis was wrong, state it explicitly: "correction: the cause is not X as I thought, reopening the analysis" — then restart.
