# persistmind

> Persistent memory framework for Claude Code. Your AI companion remembers who you are, what you decided, and why — across sessions, projects, and time.

**Status:** v0.1.0 in development. Not yet released.

## What it does

persistmind is a Claude Code plugin that turns Claude into a long-term collaborator:

- **Captures** facts, decisions, pivots, and feedback as you work, via slash commands or skills that watch the conversation.
- **Stores** them as typed Markdown fragments — human-readable, grep-able, versionable.
- **Recalls** them automatically at the start of every session (hooks inject relevant context) and on-demand (semantic search via [basic-memory](https://memory.basicmachines.co/)).
- **Organizes** them in three layers: user-global (you), per-project (the work), observation buffer (passive capture).

No vendor lock-in. No black-box vectors. Memory is plain files you own.

## Architecture

Three layers:

1. **User global** — `~/.claude/memory/persistmind/` — who you are, universal preferences, cross-project rules.
2. **Project** — `~/.claude/projects/<slug>/memory/` — decisions, pivots, constraints for the current codebase.
3. **Observation buffer** — passive capture, queryable on demand.

Backbone: [basic-memory](https://github.com/basicmachines-co/basic-memory) MCP server, auto-installed via the plugin manifest.

## Install

> Pre-release. Installation flow under construction. Will be available via the official Claude Code marketplace and direct GitHub install.

```bash
/plugin install persistmind
/pm-init
```

## Slash commands (preview)

| Command | What it does |
|---|---|
| `/pm-init` | First-run wizard: identity, language, default rules |
| `/pm-remember "..."` | Capture a fact in the current project |
| `/pm-remember-global "..."` | Capture a rule globally (all projects) |
| `/pm-checkpoint` | End-of-session: propose what to save before `/clear` |
| `/pm-recall <topic>` | Semantic search across all memory layers |
| `/pm-promote <name>` | Promote a project memory to global |
| `/pm-distill` | Reduce a long conversation to its consolidated facts |
| `/pm-forget <name>` | Remove a memory after confirmation |

## Design principles

- **Files over databases.** Markdown fragments with YAML frontmatter. No proprietary format.
- **Typed memories.** `user`, `feedback`, `project`, `decision`, `pivot`, `reference` — each with a documented shape.
- **Explicit writes.** Only slash commands write memory. Skills can read but never silently persist.
- **Cross-platform.** macOS and Linux.

## License

MIT — see [LICENSE](./LICENSE).

## Status & contributing

Pre-1.0. Breaking changes possible until v0.1.0 ships. See [CONTRIBUTING.md](./CONTRIBUTING.md) and [CHANGELOG.md](./CHANGELOG.md).
