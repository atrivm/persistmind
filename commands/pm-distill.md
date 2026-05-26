---
description: Distill the current conversation into a list of consolidated facts (without saving)
argument-hint: "(optional) focus area"
---

# /pm-distill — Conversation distillation

Extract from the current conversation only the consolidated facts, in a concise and actionable form. Do NOT save anything — produce a readable report only.

**Optional focus:** $ARGUMENTS

## Procedure

1. **Scan the session.** Mentally re-read the conversation.

2. **Extract and categorize:**
   - **Decisions** (what, why, alternatives)
   - **Facts** consolidated about the project (things now true)
   - **Pivots** (direction changes)
   - **Rules** that emerged (things Claude should remember to do/not do)
   - **References** mentioned (URLs, commands, paths)

3. **Filter out noise.** Exclude:
   - Failed attempts that produced no useful learning.
   - Generic conversational phrases.
   - Clarifying questions already resolved.

4. **Present in structured format:**

```markdown
# Session distillation — <date>

## Decisions
- ...

## Consolidated facts
- ...

## Pivots
- ...

## Rules that emerged
- ...

## References
- ...
```

5. **Do not save anything.** Output only.

6. **Suggest at the end of output:** "To save these entries, use `/pm-checkpoint`. For individual entries, use `/pm-remember` or `/pm-remember-global`."

## When to use
- To take stock mid-session.
- Before a meeting, to bring a summary.
- When you want to see "what have we concluded?" without yet committing to a save.
