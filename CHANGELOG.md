# Changelog

All notable changes to persistmind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-09-01

### Fixed

- Newly registered basic-memory projects were never indexed for semantic search: running `basic-memory mcp` watchers only cover projects that existed at startup, so fragments saved to a brand-new project were injected via hooks but invisible to `/pm-recall` (silent failure). `/pm-remember` and `/pm-checkpoint` now run `basic-memory reindex --project <name>` right after `project add` / after writing fragments, and verify with `basic-memory status`.

## [0.3.0] - 2026-08-18

### Added

- **Multi-account support.** Hooks and slash commands now honor the `CLAUDE_CONFIG_DIR` and `BASIC_MEMORY_CONFIG_DIR` env vars, so a wrapper alias (e.g. `claude-work="CLAUDE_CONFIG_DIR=~/.claude-work BASIC_MEMORY_CONFIG_DIR=~/.basic-memory-work claude"`) gets per-account project memories and observations while sharing the global layer. Project paths follow `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/...`; the basic-memory config path follows `${BASIC_MEMORY_CONFIG_DIR:-~/.basic-memory}/config.json`. Defaults preserve the single-account behavior exactly.
- `/pm-remember` now auto-registers the current project in basic-memory (idempotent, best-effort) on first save, so semantic search picks up new project memories without a manual `basic-memory project add` step.

### Changed

- `hooks/inject_memory_context.py` and `hooks/capture_observation.py` derive their basic-memory config path and per-account project root from env vars instead of hardcoding `~/.basic-memory/config.json` and `~/.claude/projects/...`.
- All `pm-*` commands and observer skills document a `$CLAUDE_DIR` path convention and resolve project paths from it. The global layer (`~/.claude/memory/persistmind/`) and `CLAUDE.md` block remain hardcoded — shared across accounts by design.
- `/pm-init` step 3g pre-creates and registers the observation buffer under `$CLAUDE_DIR/observations/` instead of the fixed `~/.claude/observations/`.

### Fixed

- **Pinned memories now inject their full body.** The `UserPromptSubmit` hook used to emit a bare pointer line ("read the file for details") for `always_inject: true` memories, which carried no behavioral weight — the model almost never opened the file, so pinned rules were routinely ignored. The hook now injects the frontmatter-stripped body of each pinned memory (capped at 3500 chars) under an imperative "standing user instructions" header, and handles the doubled frontmatter blocks that basic-memory sync can prepend.

## [0.2.0] - 2026-05-27

### Added

- **Observation buffer (Layer 3) is now implemented.** A `SessionEnd` hook (`hooks/capture_observation.sh`) writes one deterministic Markdown note per session — user prompts, per-tool usage counts, and files touched — into `~/.claude/observations/<project-slug>/`, registered as the `persistmind-observations` basic-memory project and searchable via `/pm-recall`. No LLM runs in the hook.
- `hooks/hooks.json` manifest that wires all lifecycle hooks to events. Previously the hook scripts shipped but were not bound to any event, so they never fired on a fresh install.
- `/pm-init` now pre-creates and registers the observation buffer (step 3g).
- Environment overrides: `PM_OBSERVATIONS_PROJECT` (default `persistmind-observations`) and `PM_OBSERVATIONS_ROOT` (default `~/.claude/observations`).

### Changed

- The `UserPromptSubmit` injection hook now skips the observations project when scanning for pinned memories, so the growing buffer never slows prompt-time injection.
- README and `docs/ARCHITECTURE.md` updated: the third layer now documents a real path and capture/recall flow; basic-memory's AGPL-3.0 license and arms-length dependency relationship are noted.

### Fixed

- `block_dangerous_git` no longer blocks a plain `git push origin main`. The leading-`+` force-refspec check is now scoped to a `+` adjacent to the ref (e.g. `+main`), so an unrelated `+` elsewhere in a compound command (such as inside an `echo`) no longer triggers a false positive.

## [0.1.0] - 2026-05-26

First public release.

### Added

- Three-layer memory architecture: user-global, per-project, and observation buffer.
- 8 slash commands: `/pm-init`, `/pm-remember`, `/pm-remember-global`, `/pm-checkpoint`, `/pm-recall`, `/pm-promote`, `/pm-distill`, `/pm-forget`.
- 6 observer skills (`pm-` prefixed) that propose captures and never write without confirmation.
- Deterministic lifecycle hooks: memory injection on every prompt, checkpoint reminder on session stop, git-safety guard, and version-bump guard.
- `/pm-init` setup wizard: language and feedback-rule selection; writes a managed block to `~/.claude/CLAUDE.md` between `<!-- PERSISTMIND START/END -->` markers.
- Template catalog of 10 universal feedback rules.
- Semantic search and cross-project recall via the [basic-memory](https://github.com/basicmachines-co/basic-memory) MCP backbone.
- Marketplace manifest for one-command install via the `atrivm` marketplace.
