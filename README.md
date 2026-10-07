# persistmind

> Persistent memory framework for Claude Code. Your AI companion remembers who you are, what you decided, and why — across sessions, projects, and time.

**Status:** v0.6.0 — no basic-memory, no MCP server, no index: recall is a word search over the memory files and the observation buffer (`scripts/recall.sh`).

## What it does

persistmind is a Claude Code plugin that turns Claude into a long-term collaborator:

- **Captures** facts, decisions, pivots, and feedback as you work, via slash commands or observer skills.
- **Stores** them as typed Markdown fragments — human-readable, grep-able, versionable.
- **Recalls** them at every session start (pinned rules linked into `~/.claude/rules/`, the project's `MEMORY.md` index) and on demand (a word search across every layer, `/pm-recall`).
- **Organizes** them in three layers: user-global, per-project, observation buffer.

No vendor lock-in. No black-box vectors. Memory is plain files you own.

## Architecture at a glance

Three layers:

1. **User global** — `~/.claude/memory/persistmind/` — who you are, universal preferences, cross-project rules.
2. **Project** — `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<slug>/memory/` — decisions, pivots, constraints for the current codebase (per-account in multi-account setups, e.g. `~/.claude-work/projects/...` for a `claude-work` wrapper alias).
3. **Observation buffer** — `~/.claude/observations/` — one auto-captured note per session (prompts, tools, files touched), searchable via `/pm-recall`, never auto-injected.

No database and no background service: the memory is the Markdown files, and recall searches them by words.

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
- macOS or Linux. Windows is not supported.

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
| `/pm-recall <topic>` | Word search across every memory layer |
| `/pm-promote <name>` | Promote a project memory to global |
| `/pm-distill` | Reduce a long conversation to consolidated facts (read-only) |
| `/pm-forget <name>` | Remove a memory after confirmation (backed up first) |

## Observer skills

Six skills watch the conversation and propose captures when relevant — nothing is saved without your confirmation:

- **`pm-memory-curator`** — drafts free-form input into typed fragments
- **`pm-session-onboarding`** — produces a brief from memory at session start
- **`pm-knowledge-recall`** — answers "did we already…?" by searching the memory files
- **`pm-decision-logger`** — proposes `decision` memories when you settle a choice
- **`pm-pivot-detector`** — proposes `pivot` memories when direction changes
- **`pm-memory-audit`** — checks for stale entries, duplicates, orphans, conflicts

## Safety hooks

Four deterministic hooks bind to Claude Code lifecycle events (wired in `hooks/hooks.json`):

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

v0.6.0. Pre-1.0, so breaking changes are possible between minor versions until 1.0.
