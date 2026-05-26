---
name: no-version-bump
description: Never bump version fields (package.json, Cargo.toml, pyproject.toml, pubspec.yaml, etc.) without an explicit request
type: feedback
tags:
  - git
  - releases
  - config
---

Never bump the `version` field in configuration files (`package.json`, `Cargo.toml`, `pyproject.toml`, `pubspec.yaml`, `__init__.py`, `setup.py`, etc.) unless the user explicitly asks.

**Why:** A version bump is a deliberate release action. Bumping it as part of "cleanup" or as an automated pattern causes unintended releases and confusion in changelogs and git tags.

**How to apply:** If an Edit or Write touches the `version` field, stop and ask for confirmation. The rule applies even during refactors or when editing other fields in the same file.
