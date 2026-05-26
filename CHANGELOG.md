# Changelog

All notable changes to persistmind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
