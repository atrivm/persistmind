#!/usr/bin/env bash
# PostToolUse (Write/Edit) and SessionStart hook — reindexes basic-memory
# projects in the background, one run at a time. Forwards stdin (Claude Code
# JSON event) and arguments to the Python implementation.
exec python3 "$(dirname "$0")/reindex_memory.py" "$@"
