---
name: pm-pivot-detector
description: When during a session the conversation reveals a change of direction — abandoning a previously chosen approach, switching technologies, restructuring architecture, or reversing a recent decision. Phrases like "let's change direction", "this isn't working, let's try Y", "drop X", "on second thought", "stop, change approach", "let's rewind", "let's go back on", or detecting that a previously documented `decision` is being contradicted. Proposes to save a `pivot` memory.
metadata:
  version: 1.0.0
---

# Pivot Detector — Capture direction changes

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

When the flow changes direction relative to a previous choice, propose saving it as a pivot in memory.

## Trigger patterns

- "let's change direction"
- "not working, let's try Y"
- "drop X"
- "on second thought..."
- "stop, change approach"
- "let's go back on X"
- "X wasn't working, going with Y"
- Detection: the user is contradicting a previous `decision_*.md` of this project.

Recognize the equivalent phrases in the user's working language.

## Procedure

1. **Detect the pivot.**

   Two paths:
   - **Explicit**: the user uses one of the phrases above.
   - **Implicit**: compare the conversation against the project's existing `decision_*.md`. If you detect a contradiction (e.g. memory says "we picked React", conversation says "using SvelteKit instead"), trigger.

2. **Do NOT interrupt abruptly.** Wait for the idea to settle (1-2 follow-up turns).

3. **Propose the save:**

   ```
   Pivot detected: we're moving away from <X> toward <Y>.

   Previous memory: `decision_<old-slug>` (created on <date>) — want me to mark it as superseded?
   Want to save the pivot as `pivot_<slug>`?
   ```

4. **If confirmed**, collect:
   - **Date:** today
   - **From:** <previous state, optionally with a reference to the superseded memory>
   - **To:** <new state>
   - **Trigger:** what caused it (error? discovery? new constraint?)
   - **Impact:** what changes from here

5. **Create the file** `$CLAUDE_DIR/projects/<slug>/memory/pivot_<slug>.md` via the `pm-memory-curator` skill.

6. **Update the superseded memory.** If it exists, add to its frontmatter:
   ```yaml
   metadata:
     ...
     superseded_by: pivot_<slug>
     superseded_at: <date>
   ```
   And prepend a notice at the top of the body: `> **SUPERSEDED** by [[pivot_<slug>]] on <date>.`

7. **Update the project's MEMORY.md.** Add a `## Pivots` section if it doesn't exist.

## Constraints

- Never label a minor change as a pivot (e.g. renaming a variable). Pivot = change of approach/technology/architecture.
- Never overwrite the previous memory: it must remain consultable for historical audit, but marked as superseded.
- If the user is only brainstorming alternatives but hasn't actually decided, do NOT trigger. Wait for a settled choice.

## Example

Existing memory: `decision_use-langgraph` — "We'll use LangGraph as the multi-agent orchestrator."

Conversation:
> User: LangGraph cost has exploded, €60/run. Let's try custom Claude Code skills.
> Claude: [analyzes]
> User: ok, dropping LangGraph, rewriting as skills.

Trigger! Propose:
```
Pivot detected: dropping LangGraph in favor of Claude Code skills.
Previous memory `decision_use-langgraph` → I'll mark it as superseded.
Save as `pivot_langgraph-to-skills`?
```
