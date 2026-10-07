---
name: pm-knowledge-recall
description: When the user references past work or asks if something was previously discussed, decided, or built — phrases like "did we already do X?", "did we decide on Y?", "remember when...", "did we try...", "was there a solution for...", "I don't remember if...", "have we seen this error before?". Searches every memory layer by words (global, all projects, observation buffer), reads the best matches and answers from them.
metadata:
  version: 1.0.0
---

# Knowledge Recall — Cross-session memory lookup

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

When the user wonders if something has already been done/seen/decided, search the memory files and surface what memory knows.

## Trigger patterns (recognize these formulations)

- "did we already do X?"
- "remember when...?"
- "we decided..."
- "we tried..."
- "I don't remember if..."
- "was there a solution for..."
- "have we seen this error before?"
- "in the past..."
- "a few sessions ago..."

Recognize the equivalent phrases in the user's working language.

## Procedure

1. **Build the pattern.** From the user's sentence pull 3-8 words a memory about it would contain: nouns, specific verbs, technical identifiers, their synonyms, and the same words in the other language the user writes in (Italian and English here). Use stems for plurals and variants (`proiettor` matches proiettore and proiettori). Discard conversational filler ("did we", "remember", etc.). Join them with `|`.

2. **Search** via Bash, adding as extra arguments any other memory folder the user's `CLAUDE.md` lists for the active account:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/recall.sh" '<word1>|<word2>|<word3>'
   ```
   It searches the global layer, every project memory of `$CLAUDE_DIR` and its observation buffer. Each output line is: matching lines, file path, description; files with more matching lines come first.

3. **Retry once if thin.** No result, or only weak ones: search again with other words (synonyms, the other language, a broader term).

4. **Read the best matches.** Open the 2-4 most promising files and answer from their content. Notes under `observations/` record a past session (prompts, files touched); the date is in their file name.

5. **Compose the answer:**

   If ≥1 relevant matches:
   ```markdown
   **Yes, there's memory on this:**

   1. **<title>** (<scope>, <type>)
      <2-3 line excerpt>

   2. **<title>** (...)
      <excerpt>

   ...

   Want me to open the full file of one of these? Or want to `/pm-promote` one that should be global?
   ```

   If no relevant match:
   ```markdown
   **No memory match for this topic.**

   Possible reasons:
   - We haven't saved it yet (want to `/pm-remember` or `/pm-remember-global`?)
   - We discussed it but didn't consolidate (it was an ephemeral conversation)
   - The search pattern was too specific — let me retry with synonyms: "<alt keywords>"

   <retry with synonyms if it makes sense>
   ```

## Constraints

- Do not invent matches. If there's nothing, say so clearly.
- Maximum 5 results in the first pass. If the user wants more, run a second targeted query.
- Always include the SCOPE (global / project name) for each hit — it clarifies where the memory lives.
- If you find a memory from project X while the user is working on Y, flag it: "This memory is from project X — possibly a candidate for `/pm-promote` to global."
