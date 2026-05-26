---
name: time-awareness
description: Anchor session date via `date` at start, and convert relative dates to absolute YYYY-MM-DD before saving memories
type: feedback
tags:
  - time
  - memory
  - dates
---

**At session start:** run `date '+%A %d %B %Y, %H:%M:%S %Z'` via Bash to anchor the current date as active context.

**When saving memories** (feedback / decision / project / pivot / reference) and the content contains relative dates the user mentioned, **convert them to absolute dates** before writing.

| What the user said | What to write in memory |
|---|---|
| "yesterday" | `2026-05-22` (if today is 2026-05-23) |
| "last week" | `week of 2026-05-12` |
| "in 24h" | `2026-05-24` |
| "next Thursday" | `2026-05-28` |
| "last month" | `April 2026` |

**Why:** Memories outlive the current session. Tomorrow "yesterday" is today, and in a week it's completely ambiguous. Absolute dates stay readable at 6-month distance, and let audit scripts flag stale entries (`mtime` or `created` field).

**How to apply:**
- A decision taken "yesterday"? Compute the date and write `created: 2026-05-22` or "taken on 2026-05-22".
- "Merge freeze starts Thursday"? Memory: "freeze begins 2026-05-28".
- For the frontmatter `created` field: always today's date in `YYYY-MM-DD`.
- If the user did not specify and you cannot infer, default to today.
