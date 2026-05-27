# Architecture

This document explains how persistmind is structured, where memory lives on disk, and how the pieces fit together. It is written for contributors and curious users. For day-to-day usage, see [USAGE.md](./USAGE.md).

## Mental model

persistmind treats long-term memory as a **layered store of typed Markdown fragments**. Three layers, each with a clear purpose:

| Layer | Path | Holds |
|---|---|---|
| **User global** | `~/.claude/memory/persistmind/` | Identity, universal preferences, cross-project rules |
| **Project** | `~/.claude/projects/<slug>/memory/` | Decisions, pivots, constraints scoped to one codebase |
| **Observation buffer** | `~/.claude/observations/` | One auto-captured note per session — searchable, never auto-injected |

Each layer is a directory of `.md` files. The top of each layer has a `MEMORY.md` index that the Claude Code harness always loads. Fragment files are loaded on demand (by the user, by hooks, or via semantic search).

The split exists so that a rule learned in one project (e.g. "never `--no-verify`") can live globally and apply everywhere, while a rule specific to one codebase (e.g. "migrations must be reversible") stays in that project's scope.

## Storage layout

```
~/.claude/
├── CLAUDE.md                          # User global instructions (persistmind manages a delimited block)
├── memory/
│   └── persistmind/                   # User global memory layer
│       ├── MEMORY.md                  # Index (always loaded)
│       └── *.md                       # Typed fragments (loaded on demand)
├── projects/
│   └── <project-slug>/
│       └── memory/
│           ├── MEMORY.md              # Project index (always loaded for that project)
│           └── *.md                   # Project-scoped fragments
├── observations/                      # Layer 3 — passive session capture
│   └── <project-slug>/
│       └── <date>-<session-id>.md     # One note per session (searchable, never auto-injected)
└── backups/                           # /pm-forget writes here before deletion
```

`<project-slug>` is the Claude Code project identifier — derived from the working directory path.

## Observation buffer (Layer 3)

The `SessionEnd` hook (`hooks/capture_observation.sh`) writes one Markdown note per session into `~/.claude/observations/<project-slug>/`. It is **deterministic**: it parses the session transcript and records what is already there — the user prompts, a per-tool usage count, and the files touched (`Edit`/`Write`/`MultiEdit`/`NotebookEdit`). No LLM runs in the hook; intelligent distillation stays the job of `/pm-checkpoint`.

These notes are registered as the `persistmind-observations` basic-memory project, so `/pm-recall` searches them alongside the curated layers. They are deliberately **excluded** from prompt-time injection (the `UserPromptSubmit` hook skips this project) and from the always-loaded indexes — the buffer is queried on demand, not pushed into every prompt. Sessions with no real user prompts are skipped to avoid noise.

## Memory format

Every memory is a Markdown file with YAML frontmatter. The frontmatter is a contract; the body is free-form but follows a per-type shape.

### Frontmatter

```yaml
---
name: kebab-case-slug
description: One-line summary used for relevance ranking
metadata:
  type: user | feedback | project | decision | pivot | reference
  created: YYYY-MM-DD
  tags: [optional, list]
  always_inject: false   # opt-in; true means "inject on every prompt"
---
```

### Types and body shapes

- **`user`** — facts about the human (role, stack, preferences). Body: free-form description.
- **`feedback`** — operational rules ("don't do X", "always do Y"). Body: rule, then `**Why:**` (motivation), then `**How to apply:**` (when it triggers).
- **`project`** — facts about ongoing work, deadlines, stakeholders. Body: fact, then `**Why:**` and `**How to apply:**`.
- **`decision`** — an architectural or technical choice. Body: what was decided, why, alternatives discarded, whether reversible.
- **`pivot`** — a change of direction superseding an earlier decision. Body: date, from → to, trigger, impact.
- **`reference`** — pointer to an external resource (Linear board, dashboard, doc). Body: what it is, URL/path, when to consult.

Fragments link to each other with `[[slug]]` wiki-link syntax. A `[[slug]]` that does not resolve yet is fine — it marks a memory worth writing later.

## Plugin manifest

persistmind is a standard Claude Code plugin. Two manifest files at the repo root:

### `.claude-plugin/plugin.json`

Declares metadata: name, version, description, author, keywords. The Claude Code marketplace and `/plugin install` use this.

### `.mcp.json`

Declares the MCP server stack the plugin depends on. persistmind registers exactly one:

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "basic-memory",
      "args": ["mcp"]
    }
  }
}
```

[basic-memory](https://github.com/basicmachines-co/basic-memory) is the semantic search backbone — it indexes the Markdown fragments and exposes search/recall via MCP tools. The plugin assumes `basic-memory` is on `$PATH` (configurable via `PM_BASIC_MEMORY_BIN`).

## Components

### Slash commands (`commands/`)

Eight user-facing commands. They are the **only** code paths authorized to write memory fragments.

| Command | Role |
|---|---|
| `/pm-init` | First-run wizard: language and default feedback rules |
| `/pm-remember` | Capture a fact in the current project |
| `/pm-remember-global` | Capture a rule in the user global layer |
| `/pm-checkpoint` | End-of-session: analyze conversation, propose what to save |
| `/pm-recall` | Semantic search across all layers |
| `/pm-distill` | Reduce a long conversation to consolidated facts (read-only) |
| `/pm-promote` | Move a project memory to the global layer |
| `/pm-forget` | Remove a memory after confirmation (backed up first) |

### Skills (`skills/`)

Six observer skills. They **read** the conversation and **propose** captures, but they never silently persist — every save goes through `/pm-remember` / `/pm-remember-global` after user confirmation.

| Skill | Triggers on |
|---|---|
| `pm-memory-curator` | Any save intent — reshapes free-form input into typed fragment |
| `pm-session-onboarding` | Session start with no specific task — produces brief from memory |
| `pm-knowledge-recall` | "Did we already…?" / "Remember when…?" — semantic search |
| `pm-decision-logger` | Detected architectural choice — proposes a `decision` memory |
| `pm-pivot-detector` | Direction change contradicting a prior decision — proposes a `pivot` |
| `pm-memory-audit` | "Clean up memory" / "any contradictions?" — stale/dup/conflict checks |

### Hooks (`hooks/`)

Five deterministic hooks bound to Claude Code lifecycle events.

| Hook | Event | Purpose |
|---|---|---|
| `inject_memory_context.sh` → `.py` | `UserPromptSubmit` | Injects pinned memories (`always_inject: true`) + top semantic hits as context |
| `capture_observation.sh` → `.py` | `SessionEnd` | Writes one deterministic note per session into the observation buffer (Layer 3) |
| `propose_checkpoint.sh` | `Stop` | Cross-platform notification suggesting `/pm-checkpoint` before `/clear` |
| `block_dangerous_git.sh` | `PreToolUse` (Bash) | Blocks `--no-verify`, force-push on main, `--no-gpg-sign`, `Co-Authored-By` |
| `block_version_bump.sh` | `PreToolUse` (Edit/Write) | Blocks unintended version bumps in package manifests |

The `block_*` hooks are opinionated safety nets — they enforce rules persistmind teaches as feedback memories, so they keep working even when a model forgets a rule mid-session.

### Templates (`templates/rules/`)

Ten universal `feedback`-type rule templates installed by `/pm-init` if the user opts in. They cover code style, git safety, type discipline, investigation rigor. Each is a complete fragment ready to drop into the global layer — `/pm-init` adds the `created:` field at install time.

## Capture flow

```
User intent → slash command → pm-memory-curator skill → typed fragment → MEMORY.md index updated → basic-memory auto-sync
```

Three invariants:

1. **Only slash commands write.** Skills, hooks, and other MCP tools may read memory but cannot persist it. This makes capture auditable.
2. **The MEMORY.md index is the source of truth for what's loaded automatically.** A fragment file without an index entry is effectively invisible at session start (but still findable via search).
3. **Writes are user-confirmed.** Even when a skill proposes a save, the user sees the draft and approves before disk write.

## Recall flow

Two paths:

**Automatic, every prompt.** `UserPromptSubmit` hook runs `inject_memory_context.py`, which:
1. Loads all fragments with `always_inject: true` (pinned rules).
2. Runs a basic-memory semantic search against the user's prompt across the global layer and the current project's layer.
3. Injects the top hits as a `## Auto-injected memories` block above the user prompt.

**On-demand, explicit.** `/pm-recall <topic>` runs a cross-project semantic search (every registered basic-memory project) and surfaces the top-ranked hits with scope and excerpt.

## Cross-platform behavior

persistmind targets macOS and Linux. OS-specific code paths:

- **Notifications** (`propose_checkpoint.sh`): branches on `$(uname)` — `osascript` on Darwin, `notify-send` on Linux, falls back to `stderr` if neither is available.
- **Paths**: always derive from `$HOME` / `~`. No hardcoded absolute paths.
- **No BSD-only `sed` flags.** Use portable forms.

Windows is not supported.

## Environment variables

Two env vars let you override defaults without editing plugin files:

| Var | Default | Purpose |
|---|---|---|
| `PM_GLOBAL_PROJECT` | `persistmind-global` | Name of the basic-memory project that backs the user global layer |
| `PM_BASIC_MEMORY_BIN` | `basic-memory` | Binary name or path to invoke basic-memory (useful if installed via pipx with a non-`PATH` shim) |

Set them in your shell rc file or in Claude Code's environment.

## Design principles

- **Files over databases.** Markdown + YAML. You can read, grep, version-control, and migrate memory with standard tools.
- **Typed fragments.** Each type has a documented shape so future memories stay consistent with past ones.
- **Explicit writes.** Capture is always user-confirmed. No silent persistence.
- **Layered scope.** Rules live as high up the stack as they generalize — and `/pm-promote` is the only path from project to global.
- **Boring infrastructure.** A shell hook, a Python script, a Markdown file. No process supervisor, no daemon, no proprietary store.

## Further reading

- [USAGE.md](./USAGE.md) — workflows and command-by-command walkthrough.
- [CONTRIBUTING.md](../CONTRIBUTING.md) — development setup and conventions.
- [basic-memory docs](https://memory.basicmachines.co/) — the MCP backbone.
