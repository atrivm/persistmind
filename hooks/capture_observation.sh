#!/usr/bin/env bash
# SessionEnd hook — Layer 3 (observation buffer).
# Writes one compact Markdown note per session. Forwards stdin (Claude Code
# JSON event) to the Python implementation.
exec python3 "$(dirname "$0")/capture_observation.py"
