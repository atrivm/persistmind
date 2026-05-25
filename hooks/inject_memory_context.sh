#!/usr/bin/env bash
# UserPromptSubmit hook — inietta memorie pinnate + semanticamente rilevanti.
# Forwards stdin (Claude Code JSON event) to the Python implementation.
exec python3 "$(dirname "$0")/inject_memory_context.py"
