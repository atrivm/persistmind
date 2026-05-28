---
name: pm-decision-logger
description: When the user makes an explicit architectural or technical decision during the session — phrases like "let's go with X", "we'll use Y", "we picked Z", "we're choosing A over B", "we're dropping X", "moving forward with...", "preferring Y to X", or when Claude detects a clear choice being made between alternatives. After the decision is taken, this skill proposes to save it as a typed `decision` memory.
metadata:
  version: 1.0.0
---

# Decision Logger — Architectural decision capture

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

When a decision is made, propose to the user that you save it to memory along with the why.

## Trigger patterns

- "let's go with X"
- "we'll use Y"
- "we picked..."
- "we're choosing..."
- "we're dropping X"
- "we prefer X to Y"
- A conversation like "let's evaluate A vs B" that concludes with "OK, A".

Recognize the equivalent phrases in the user's working language.

## Procedure

1. **Recognize the decision.** Even implicit ones: if you were evaluating 2-3 options and are now proceeding with one, there's a decision to log.

2. **Do NOT interrupt the flow immediately.** Wait for the decision moment to settle (the next message, or when the topic shifts).

3. **Propose the save:**
   ```
   I see we've decided: <X>.
   Want me to save it as a `decision` memory? (suggested scope: project)
   ```

4. **If the user confirms**, collect (ideally from context, otherwise ask):
   - **What:** the decision
   - **Why:** rationale (constraints, data, experience)
   - **Discarded alternatives:** which other options were on the table and why not
   - **Reversible?:** yes/no and with what effort

5. **Generate the fragment** via the `pm-memory-curator` skill (type: decision).

6. **Save** to `$CLAUDE_DIR/projects/<slug>/memory/decision_<slug>.md`.

7. **Update the project's MEMORY.md index.**

## Constraints

- Never force the save. If the user says "no", drop it. Memory is opt-in.
- Never log decisions that are not yet confirmed ("maybe we'll use X" is not a decision).
- If the user confirms 3 decisions back-to-back in one message, group them into a single multi-select proposal.
- Never save credentials, passwords, or secret configurations as "decisions".

## Example

Conversation:
> User: we need to pick between Postgres and SQLite for persistence. Heavy concurrent writes, but single-machine.
> Claude: [pros/cons analysis]
> User: ok let's go with Postgres, single-machine for now, read replicas later.

Trigger! Propose:
```
Decision detected: use Postgres (not SQLite) for persistence.
Save it as `decision_postgres-over-sqlite`?
```
