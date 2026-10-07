---
description: Search every memory layer by words (global, projects, observation buffer)
argument-hint: "<topic or question>"
---

# /pm-recall — Search memories by words

Find the memories most relevant to the query across the global layer, every project memory of the active account and its observation buffer.

**Query:** $ARGUMENTS

## Procedure

1. **Build the pattern.** Pick 3-8 words a memory about the topic would contain: the key nouns and identifiers, their synonyms, and the same words in the other language the user writes in (Italian and English here). Use stems to cover plurals and variants (`proiettor` matches proiettore and proiettori). Join them with `|`.

2. **Search** via Bash. Add as extra arguments any other memory folder the user's `CLAUDE.md` lists for the active account:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/recall.sh" '<word1>|<word2>|<word3>'
   ```
   Each output line is: matching lines, file path, description. Files with more matching lines come first.

3. **Retry once if thin.** No result, or only weak ones: search again with other words (synonyms, the other language, a broader term).

4. **Read before answering.** Open the 2-4 most promising files and answer from what they say, not from the description alone. Notes under `observations/` record a past session (prompts, files touched); the date is in their file name.

5. **Present** the results as a Markdown table:

| # | Scope | File | Why it matches |
|---|---|---|---|

Scope is `global` for `~/.claude/memory/`, the project name for `projects/<slug>/memory/`, `observations` for the observation buffer.

## Suggest follow-up actions when relevant
- "Want me to open the full file?"
- "Worth `/pm-promote <slug>`? This rule is universal but lives only in one project."
- "No match → want me to `/pm-remember-global <topic>` to write it?"

## Constraints
- Maximum 10 rows in the table.
- Do not invent matches: if nothing fits, say so and list the words you searched.
