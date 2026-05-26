# Usage

This document walks through the typical workflows: setting up, capturing memory as you work, recalling it later, and maintaining the store over time. For the internal model and component breakdown, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Prerequisites

- Claude Code installed and configured.
- [basic-memory](https://memory.basicmachines.co/) on `$PATH` (`pipx install basic-memory` is the easiest path).
- macOS or Linux.

Verify:

```bash
basic-memory --version
```

If `basic-memory` is installed somewhere not on `$PATH`, point persistmind at it:

```bash
export PM_BASIC_MEMORY_BIN=/full/path/to/basic-memory
```

## First-time setup

Install the plugin, then bootstrap:

```bash
/plugin install persistmind
/pm-init
```

`/pm-init` is a 3-step interactive wizard:

1. **Identity** — who you are (role, primary tech stack, display name).
2. **Language** — the language you want Claude to respond in. Code, identifiers, and commit messages stay English regardless; only the conversational layer follows your choice.
3. **Rule selection** — pick which of the 10 universal feedback rules to install in your global layer. Sensible defaults are pre-selected.

The wizard writes:

- A `<!-- PERSISTMIND START -->` ... `<!-- PERSISTMIND END -->` block in `~/.claude/CLAUDE.md` containing your identity and language preference. The block is idempotent — running `/pm-init` again replaces it without touching anything outside.
- The selected feedback rules into `~/.claude/memory/persistmind/`.
- A skeleton `MEMORY.md` index if one does not already exist.

## Capturing memory

### Ad-hoc capture

```
/pm-remember "migrations must be reversible — we got burned in Q3 when the user-table rename couldn't be rolled back"
```

`/pm-remember` saves to the **current project** layer. The `pm-memory-curator` skill takes your free-form input, identifies the type (here: `feedback`), generates a slug, drafts a `**Why:**` and `**How to apply:**` section, and shows you the result before writing.

For rules that apply across every project:

```
/pm-remember-global "always show the diff before suggesting a commit — I want to verify scope"
```

### Capture during conversation

You don't always need to type a command. Three observer skills watch the conversation and propose captures when relevant:

- **`pm-decision-logger`** — when you say "let's go with X", "we'll use Y", "we picked Z over W", it proposes a `decision` memory with what / why / alternatives / reversible.
- **`pm-pivot-detector`** — when the conversation contradicts a saved decision ("actually let's drop the queue and use webhooks instead"), it proposes a `pivot` memory and marks the old decision as superseded.
- **`pm-memory-curator`** — when you say "remember that…" without using a slash command, it routes through the same drafting pipeline.

Every proposal is shown for confirmation. Nothing is saved silently.

### End-of-session checkpoint

Before clearing context, run:

```
/pm-checkpoint
```

This scans the entire session, categorizes findings (decisions / facts / pivots / rules / references), and proposes up to 10 items with scope (project vs. global). You review the list, deselect what you don't want, and confirm. Then `/clear`.

The `propose_checkpoint.sh` hook fires on every `Stop` event with a desktop notification reminding you to do this — easy to dismiss when not relevant, easy to act on when it is.

## Recalling memory

### Automatic recall

You don't need to do anything to read pinned memories or relevant context. The `inject_memory_context.py` hook runs on every prompt and adds:

- **Pinned memories** — fragments with `always_inject: true` in frontmatter. These are loaded every turn.
- **Semantic hits** — basic-memory searches the global layer and the current project's layer against your prompt and injects the top matches.

You'll see them as a `## Memorie auto-iniettate` block above your prompt in the model's context (visible if you inspect the conversation, not in your typed input).

### Explicit recall

When you want to search yourself:

```
/pm-recall webhook retry
```

This runs across **every** registered basic-memory project (not just global + current), so you can find work from another codebase. Top 10 hits ranked by score, each with scope, excerpt, and a link to the full fragment.

The `pm-knowledge-recall` skill triggers on the same intent expressed in natural language ("did we already solve this?", "remember when we tried X?") — it runs the same search and presents results conversationally.

## Maintenance

### Promote a rule from project to global

When a rule you originally saved in one project turns out to apply everywhere:

```
/pm-promote migrations-must-be-reversible
```

The command moves the fragment from the project layer to `~/.claude/memory/persistmind/`, updates both `MEMORY.md` indices, and resyncs basic-memory.

### Distill a long conversation

```
/pm-distill
```

Read-only. Extracts the conversation's consolidated facts, decisions, pivots, rules, and references into a structured Markdown report. Nothing is saved. Useful as input for a follow-up `/pm-checkpoint` or as a handoff doc.

### Remove a memory

```
/pm-forget some-stale-rule
```

Searches both layers, backs the file up to `~/.claude/backups/`, removes it and its index entry, and warns about any `[[some-stale-rule]]` references that will become dangling.

### Audit the store

```
clean up memory
```

(Or `audit memories`, `any contradictions?`, etc. — the `pm-memory-audit` skill triggers on these phrases.)

The skill runs structural checks:

- **Stale** — fragments created >6 months ago with zero recall hits.
- **Duplicates** — fragments with cosine similarity > 0.92 (likely the same rule restated).
- **Orphans** — fragments with no `[[link]]` in or out.
- **Conflicts** — rules that contradict each other.

It proposes actions but executes nothing without confirmation.

## Multi-project workflow

Each Claude Code project gets its own memory directory under `~/.claude/projects/<slug>/memory/`. When you open a new project, the corresponding layer is loaded automatically alongside the global layer.

basic-memory tracks each project as a separate indexed collection. Cross-project search (`/pm-recall`) walks them all. The global layer is itself a basic-memory project (default name `persistmind-global`, override via `PM_GLOBAL_PROJECT`).

When starting a fresh session inside an existing project, the `pm-session-onboarding` skill produces a brief from memory: current state, recent decisions, applicable global rules, open TODOs, last checkpoint date. Triggered by an empty-handed session start or by phrases like "where did we leave off?".

## Safety hooks

Two hooks block dangerous git and config operations even when not explicitly remembered:

- **`block_dangerous_git.sh`** intercepts `Co-Authored-By` commits, `--no-verify`, `--no-gpg-sign`, and force-push on `main`/`master`.
- **`block_version_bump.sh`** intercepts version-field changes in `package.json`, `Cargo.toml`, `pyproject.toml`, `pubspec.yaml`, and friends.

Both are PreToolUse hooks — they fail loud with a message explaining what was blocked and how to override if you really meant it.

## Troubleshooting

**`basic-memory: command not found`** — install it (`pipx install basic-memory`) or set `PM_BASIC_MEMORY_BIN` to its full path.

**Memories aren't being injected on prompts.** Check that hooks are enabled in `~/.claude/settings.json`. Run `basic-memory project list` to confirm your global project and current project are both registered.

**`/pm-init` keeps duplicating the CLAUDE.md block.** It shouldn't — the block is delimited and replaced in place. If it does, file a bug with the contents of your `~/.claude/CLAUDE.md`.

**Memory feels stale.** Run the `pm-memory-audit` skill ("clean up memory") and prune.

## Next steps

- [ARCHITECTURE.md](./ARCHITECTURE.md) — internal model, storage layout, manifest format.
- [CONTRIBUTING.md](../CONTRIBUTING.md) — extend persistmind with new commands, skills, or templates.
