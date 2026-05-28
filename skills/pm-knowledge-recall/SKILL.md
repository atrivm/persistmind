---
name: pm-knowledge-recall
description: When the user references past work or asks if something was previously discussed, decided, or built — phrases like "did we already do X?", "did we decide on Y?", "remember when...", "did we try...", "was there a solution for...", "I don't remember if...", "have we seen this error before?". Triggers semantic search across all memory layers (global + all projects) and presents matching results with relevance.
metadata:
  version: 1.0.0
---

# Knowledge Recall — Cross-session memory lookup

> **Path convention:** `$CLAUDE_DIR` = `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` (active Claude Code config dir). Default `~/.claude`; multi-account setups like `claude-work` set it to `~/.claude-work`. The global layer (`~/.claude/memory/persistmind/`) stays shared regardless.

When the user wonders if something has already been done/seen/decided, run a semantic search and surface what memory knows.

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

1. **Extract the query.** From the user's sentence, pull 3-7 meaningful keywords (nouns, specific verbs, technical identifiers). Discard conversational filler ("did we", "remember", etc.).

2. **Primary semantic search.** Via the basic-memory MCP tool:
   ```
   mcp__basic-memory__search_notes(query="<keywords>", limit=10)
   ```
   If unavailable, fall back via Bash:
   ```bash
   basic-memory tool search-notes "<keywords>" | head -100
   ```

3. **Parallel text search.** To avoid false negatives, also:
   ```bash
   CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
   grep -ril -E "<keyword1>|<keyword2>" ~/.claude/memory/ "$CLAUDE_DIR"/projects/*/memory/ 2>/dev/null | head -10
   ```

4. **Dedupe and rank.** Combine the results, dedupe by file_path. Sort by score (semantic primary, then fallback recency).

5. **Relevance filter.** Drop entries with score < 0.4 (below that threshold is usually noise).

6. **Compose the answer:**

   If ≥1 relevant matches:
   ```markdown
   **Yes, there's memory on this:**

   1. **<title>** (<scope>, <type>, score <X.XX>)
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
