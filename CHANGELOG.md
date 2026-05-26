# Changelog

All notable changes to persistmind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Observation buffer (Layer 3) is now implemented.** A `SessionEnd` hook (`hooks/capture_observation.sh`) writes one deterministic Markdown note per session — user prompts, per-tool usage counts, and files touched — into `~/.claude/observations/<project-slug>/`, registered as the `persistmind-observations` basic-memory project and searchable via `/pm-recall`. No LLM runs in the hook.
- `hooks/hooks.json` manifest that wires all lifecycle hooks to events. Previously the hook scripts shipped but were not bound to any event, so they never fired on a fresh install.
- `/pm-init` now pre-creates and registers the observation buffer (step 3g).
- Environment overrides: `PM_OBSERVATIONS_PROJECT` (default `persistmind-observations`) and `PM_OBSERVATIONS_ROOT` (default `~/.claude/observations`).

### Changed

- The `UserPromptSubmit` injection hook now skips the observations project when scanning for pinned memories, so the growing buffer never slows prompt-time injection.
- README and `docs/ARCHITECTURE.md` updated: the third layer now documents a real path and capture/recall flow; basic-memory's AGPL-3.0 license and arms-length dependency relationship are noted.

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
