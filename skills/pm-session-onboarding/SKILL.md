---
name: pm-session-onboarding
description: When a new Claude Code session starts and the user has not yet given a specific task, OR when the user says "what were we doing?", "remind me where we left off", "project status", "last checkpoint", "brief". Provides a concise briefing of the current project state from memory — recent decisions, open pivots, applicable feedback rules, last checkpoint.
metadata:
  version: 1.0.0
---

# Session Onboarding — Session-opening brief

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

At the start of a session, or on request, summarize the current project state from memory so the user can resume from where they left off.

## Procedure

1. **Identify the current project.** `pwd` → slug.

2. **Load the three memory layers:**

   - **Global (User):** read `~/.claude/memory/persistmind/MEMORY.md` for the list of active cross-project rules.

   - **Project:** read `$CLAUDE_DIR/projects/<slug>/memory/MEMORY.md` (if it exists). If missing, tell the user.

   - **Recent activity:** the five most recently changed fragments of each layer, via Bash:
     ```bash
     CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
     # global
     ls -t ~/.claude/memory/persistmind/*.md | grep -v '/MEMORY.md$' | head -5
     # current project: <slug> is the cwd with every non-alphanumeric character turned into "-"
     # (e.g. /home/dev/my-project → "-home-dev-my-project")
     ls -t "$CLAUDE_DIR/projects/<slug>/memory/"*.md | grep -v '/MEMORY.md$' | head -5
     ```

3. **Compose the brief in 3 sections:**

   ```markdown
   ## Opening brief — <project>

   ### Current state
   <2-3 lines distilled from the most recent `project_*.md` files>

   ### Recent decisions
   <Top 3-5 `decision_*.md` or `pivot_*.md` sorted by `created` desc>

   ### Active rules (filtered for project relevance)
   <Top 3-5 relevant global `feedback_*.md` — e.g. if it's Flutter, show flutter-related; if Python, show python-related>

   ### Open issues / TODO (from memory)
   <Any `project_*` or `decision_*` entries with status "open" or "in progress">

   ### Last checkpoint
   <Date of the last `/pm-checkpoint` (look in the project's MEMORY.md or the filesystem mtime)>
   ```

4. **Print it to the user.** Maximum 30-40 lines total. Brevity over completeness.

5. **Close with an open question:** "Where do you want to pick up?" or "What do you want to do today?"

## When NOT to run

- The user already has a specific task in hand. In that case go straight to the task.
- `/loop` or automated sessions.
- When the context window is not yet "cold" (the user is resuming a long session).

## Constraints

- Never invent activity that is not documented.
- If there is no project memory, declare it: "No project memory found. Want me to initialize?"
- No filler ("Happy to help..."). Dry, operational brief.
