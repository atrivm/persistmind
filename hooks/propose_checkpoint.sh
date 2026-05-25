#!/usr/bin/env bash
# Stop hook — quando Claude termina una sessione (Stop event), propone /checkpoint via notifica macOS.
# Non blocca, è informativo.

set -eu

# Leggi input (lo ignoriamo, è solo un trigger)
input=$(cat 2>/dev/null || true)

# Notifica utente
/usr/bin/osascript -e 'display notification "Vuoi salvare la memoria di questa sessione? Lancia /checkpoint prima di /clear." with title "Claude Code — Memoria" sound name "Pop"' 2>/dev/null || true

# Log nell'event log
LOGDIR="${HOME}/.claude/logs"
mkdir -p "$LOGDIR"
echo "$(date -Iseconds) Stop event → checkpoint proposto" >> "$LOGDIR/checkpoint-reminders.log"

exit 0
