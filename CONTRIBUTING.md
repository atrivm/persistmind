# Contributing to persistmind

Thanks for your interest. persistmind is pre-1.0 and the API surface is still settling — open an issue before sending a large PR so we can align on direction.

## Ground rules

- **Language:** all code, comments, commit messages, docs, and command output must be in English. No exceptions.
- **Cross-platform:** code must run on macOS and Linux. No `osascript`-only paths, no BSD-only `sed` flags. When OS-specific behavior is needed (notifications, paths), branch on OS.
- **No personal data:** the repository is public. Do not commit emails, absolute home paths, or any user-specific information.
- **Surgical changes:** edit only what the task requires. No drive-by refactors, no opinionated reformatting of unrelated files.

## Development setup

Pre-release — installation and dogfooding flow not yet documented. See [docs/](./docs/) once it exists.

## Commit conventions

Conventional Commits in English:

```
feat: add /pm-init wizard
fix: handle missing basic-memory binary gracefully
docs: clarify memory layer routing in ARCHITECTURE.md
refactor: extract hook bootstrap into shared script
chore: bump CHANGELOG for v0.1.0
```

Keep subject lines under 72 characters. No `Co-Authored-By` trailers.

## Pull requests

- One PR per logical change.
- Include a test plan (manual steps reproducing the change end-to-end).
- Update `CHANGELOG.md` under `[Unreleased]`.

## Reporting issues

Please include:

- OS and version (`uname -a`).
- Claude Code version.
- `basic-memory --version`.
- Minimal reproduction.
