# persistmind

> Persistent memory framework for Claude Code. Your AI companion remembers who you are, what you decided, and why — across sessions, projects, and time.

**Status:** v0.2.0 — observation buffer (Layer 3) now wired and live.

## What it does

persistmind is a Claude Code plugin that turns Claude into a long-term collaborator:

- **Captures** facts, decisions, pivots, and feedback as you work, via slash commands or observer skills.
- **Stores** them as typed Markdown fragments — human-readable, grep-able, versionable.
- **Recalls** them automatically at the start of every prompt (hooks inject relevant context) and on-demand (semantic search via [basic-memory](https://memory.basicmachines.co/)).
- **Organizes** them in three layers: user-global, per-project, observation buffer.

No vendor lock-in. No black-box vectors. Memory is plain files you own.

## Architecture at a glance

Three layers:

1. **User global** — `~/.claude/memory/persistmind/` — who you are, universal preferences, cross-project rules.
2. **Project** — `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/memory/` — decisions, pivots, constraints for the current codebase (per-account in multi-account setups, e.g. `~/.claude-work/projects/...` for a `claude-work` wrapper alias).
3. **Observation buffer** — `~/.claude/observations/` — one auto-captured note per session (prompts, tools, files touched), searchable via `/pm-recall`, never auto-injected.

Backbone: [basic-memory](https://github.com/basicmachines-co/basic-memory) MCP server, declared in the plugin's `.mcp.json` and assumed to be on `$PATH`. basic-memory is a separate AGPL-3.0 dependency, installed independently — persistmind does not bundle or modify it.

For the full model — storage layout, fragment format, manifest, capture/recall flows — see [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Install

Add the marketplace, install the plugin, then run the setup wizard:

```bash
/plugin marketplace add atrivm/persistmind
/plugin install persistmind@atrivm
/pm-init
```

### Prerequisites

- Claude Code installed.
- `basic-memory` on `$PATH` — install with `pipx install basic-memory` (recommended) or `pip install basic-memory`.
- macOS or Linux. Windows is not supported.

### Verify

```bash
basic-memory --version
```

If `basic-memory` lives outside `$PATH`, point persistmind at it:

```bash
export PM_BASIC_MEMORY_BIN=/full/path/to/basic-memory
```

## Quick start

After `/pm-init` walks you through language and default rules:

```
# Capture a project-scoped fact
/pm-remember "use feature flags for any change touching billing"

# Capture a global rule
/pm-remember-global "always show the diff before suggesting a commit"

# Search across every memory layer and project
/pm-recall webhook retry

# End-of-session: propose what to save before /clear
/pm-checkpoint
```

For the full workflow guide, see [docs/USAGE.md](./docs/USAGE.md).

## Slash commands

| Command | What it does |
|---|---|
| `/pm-init` | First-run wizard: language and default rules |
| `/pm-remember "..."` | Capture a fact in the current project |
| `/pm-remember-global "..."` | Capture a rule globally (all projects) |
| `/pm-checkpoint` | End-of-session: propose what to save before `/clear` |
| `/pm-recall <topic>` | Semantic search across every memory layer |
| `/pm-promote <name>` | Promote a project memory to global |
| `/pm-distill` | Reduce a long conversation to consolidated facts (read-only) |
| `/pm-forget <name>` | Remove a memory after confirmation (backed up first) |

## Observer skills

Six skills watch the conversation and propose captures when relevant — nothing is saved without your confirmation:

- **`pm-memory-curator`** — drafts free-form input into typed fragments
- **`pm-session-onboarding`** — produces a brief from memory at session start
- **`pm-knowledge-recall`** — answers "did we already…?" with semantic search
- **`pm-decision-logger`** — proposes `decision` memories when you settle a choice
- **`pm-pivot-detector`** — proposes `pivot` memories when direction changes
- **`pm-memory-audit`** — checks for stale entries, duplicates, orphans, conflicts

## Safety hooks

Five deterministic hooks bind to Claude Code lifecycle events (wired in `hooks/hooks.json`):

- **Memory injection** on every prompt (pinned rules + semantic hits).
- **Observation capture** on session end (one note per session into the observation buffer).
- **Checkpoint reminder** on session stop (cross-platform notification).
- **Git safety**: blocks `Co-Authored-By`, `--no-verify`, force-push on `main`, `--no-gpg-sign`.
- **Version bump guard**: blocks unintended changes to `package.json`, `Cargo.toml`, `pyproject.toml`, `pubspec.yaml`, etc.

## Design principles

- **Files over databases.** Markdown with YAML frontmatter. No proprietary format.
- **Typed memories.** `user`, `feedback`, `project`, `decision`, `pivot`, `reference` — each with a documented shape.
- **Explicit writes.** Only slash commands write. Skills can read and propose, but never silently persist.
- **Layered scope.** Promotion from project to global is always manual.
- **Cross-platform.** macOS and Linux, no Darwin-only code paths.

## Documentation

- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) — internal model, storage layout, manifest, capture/recall flows.
- [docs/USAGE.md](./docs/USAGE.md) — workflows, command walkthrough, troubleshooting.
- [CONTRIBUTING.md](./CONTRIBUTING.md) — development setup and conventions.
- [CHANGELOG.md](./CHANGELOG.md) — release notes.

## License

MIT — see [LICENSE](./LICENSE).

## Status

v0.2.0. Pre-1.0, so breaking changes are possible between minor versions until 1.0.
