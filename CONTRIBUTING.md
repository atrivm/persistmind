# Contributing to persistmind

Thanks for your interest. persistmind is pre-1.0 and the API surface is still settling — open an issue before sending a large PR so we can align on direction.

## Ground rules

- **Language:** all code, comments, commit messages, docs, and command output must be in English. No exceptions.
- **Cross-platform:** code must run on macOS and Linux. No `osascript`-only paths, no BSD-only `sed` flags. When OS-specific behavior is needed (notifications, paths), branch on OS.
- **No personal data:** the repository is public. Do not commit emails, absolute home paths, or any user-specific information.
- **Surgical changes:** edit only what the task requires. No drive-by refactors, no opinionated reformatting of unrelated files.

## Development setup

The plugin is plain files — no build step. Two ways to work on it locally without polluting your real `~/.claude/`.

### Option A — Symlink into a sandbox profile

```bash
# Pick a sandbox HOME so your real config is untouched.
export TEST_HOME="$HOME/persistmind-sandbox"
mkdir -p "$TEST_HOME/.claude/plugins"
ln -s "$(pwd)" "$TEST_HOME/.claude/plugins/persistmind"

# Run Claude Code with the sandbox HOME.
HOME="$TEST_HOME" claude
```

Inside the sandbox session, `$CLAUDE_PLUGIN_ROOT` resolves to the symlink, so edits to your working tree are picked up on the next command invocation.

### Option B — Install into the real plugin directory

Use only if you accept that edits affect your live Claude Code. Symlink (`ln -s`) into `~/.claude/plugins/persistmind`, then restart Claude Code.

## Static validation

Run before opening a PR. No external dependencies beyond `python3` and `jq`:

```bash
# Bash syntax
for f in hooks/*.sh; do bash -n "$f"; done

# Python syntax
python3 -m py_compile hooks/*.py

# JSON validity
jq empty .claude-plugin/plugin.json .mcp.json

# Frontmatter presence (commands, skills, templates)
for f in commands/*.md skills/*/SKILL.md templates/rules/*.md; do
  head -1 "$f" | grep -q '^---$' || echo "MISS $f"
done
```

If you have `shellcheck` installed, run it on the hooks for stricter warnings:

```bash
shellcheck hooks/*.sh
```

## Manual test plan

Static validation cannot exercise the install flow, the wizard's interactive steps, or the hooks' OS-specific notification paths. Run these manually before a release.

### Install — macOS

1. Create a clean user account (System Settings → Users) or a fresh macOS VM.
2. Install Claude Code and `basic-memory` (`pipx install basic-memory`).
3. `/plugin install persistmind` (or use the symlink method above).
4. `/pm-init` — walk through all three steps. Verify:
   - `~/.claude/CLAUDE.md` gains a single `<!-- PERSISTMIND START -->` ... `<!-- PERSISTMIND END -->` block.
   - `~/.claude/memory/persistmind/` contains the chosen `feedback_*.md` files and a seeded `MEMORY.md`.
5. Re-run `/pm-init` — confirm the block is replaced in place (no duplication) and no rule file is overwritten without prompt.

### Install — Linux

1. Spin up a fresh Linux environment (Docker container with a desktop session, or a clean VM). `notify-send` available is a plus but not required — the hook falls back to stderr.
2. Repeat steps 2-5 from the macOS plan.

### Wizard end-to-end

After `/pm-init`:

- `/pm-remember "test fact"` writes a project-scoped fragment.
- `/pm-remember-global "test rule"` writes a global fragment.
- `/pm-recall test` returns both via semantic search.
- `/pm-forget <slug>` backs up to `~/.claude/backups/` before deletion.

### Hooks

- **`inject_memory_context`** — submit any prompt; verify the conversation context shows a `## Auto-injected memories` block above your input (visible by inspecting the model's view, or by checking `~/.claude/logs/` if enabled).
- **`propose_checkpoint`** — end a session; verify the OS notification fires (macOS notification center / Linux `notify-send`) or falls back to stderr.
- **`block_dangerous_git`** — try `git commit -m "test" --no-verify`; verify the hook blocks with an explanatory error.
- **`block_version_bump`** — try editing the `version` field in `package.json`; verify the hook blocks.

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
