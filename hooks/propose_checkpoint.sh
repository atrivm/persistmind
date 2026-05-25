#!/usr/bin/env bash
# Stop hook — quando Claude termina una sessione (Stop event), propone /checkpoint via notifica desktop.
# Non blocca, è informativo. Cross-platform: macOS (osascript), Linux (notify-send), fallback stderr.

set -eu

# Leggi input (lo ignoriamo, è solo un trigger)
input=$(cat 2>/dev/null || true)

TITLE="Claude Code — Memoria"
MESSAGE="Vuoi salvare la memoria di questa sessione? Lancia /checkpoint prima di /clear."

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
  echo "[${TITLE}] ${MESSAGE}" >&2
}

notify

# Log nell'event log
LOGDIR="${HOME}/.claude/logs"
mkdir -p "$LOGDIR"
echo "$(date -Iseconds) Stop event - checkpoint proposto" >> "$LOGDIR/checkpoint-reminders.log"

exit 0
