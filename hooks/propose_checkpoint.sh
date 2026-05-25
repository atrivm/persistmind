#!/usr/bin/env bash
# Stop hook — when Claude ends a session (Stop event), it suggests /pm-checkpoint via desktop notification.
# Non-blocking, purely informational.

set -eu

# Read input (ignored — this hook only reacts to the trigger).
input=$(cat 2>/dev/null || true)

TITLE="Claude Code — Memory"
MESSAGE="Want to save this session's memory? Run /pm-checkpoint before /clear."

# Cross-platform notification with graceful fallbacks.
notify() {
  case "$(uname -s)" in
    Darwin)
      if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"${MESSAGE}\" with title \"${TITLE}\" sound name \"Pop\"" 2>/dev/null || true
        return 0
      fi
      ;;
    Linux)
      if command -v notify-send >/dev/null 2>&1; then
        notify-send "${TITLE}" "${MESSAGE}" 2>/dev/null || true
        return 0
      fi
      ;;
  esac
  # Last-resort fallback: write to stderr (visible in the Claude Code console).
  echo "[${TITLE}] ${MESSAGE}" >&2
}

notify

# Event log
LOGDIR="${HOME}/.claude/logs"
mkdir -p "$LOGDIR"
echo "$(date -Iseconds) Stop event - checkpoint suggested" >> "$LOGDIR/checkpoint-reminders.log"

exit 0
