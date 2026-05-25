#!/usr/bin/env bash
# PreToolUse hook on Bash — blocca operazioni git pericolose.
# Riceve via stdin un JSON con {tool_name, tool_input.command, ...}.
# Exit 0 = permetti. Exit !=0 + stderr = blocca con quel messaggio.

set -eu

# Leggi JSON da stdin
input=$(cat)

# Estrai il comando
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Se non è un comando git, esci subito
if ! echo "$command" | grep -qE '(^|[;&|]\s*)git\b'; then
  exit 0
fi

# Regola 1: git commit con Co-Authored-By
if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qi 'Co-Authored-By'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] git commit contiene 'Co-Authored-By'.
Memoria globale: feedback_no_coauthored_by.md
Motivo: Vercel Hobby e altre CI rifiutano deploy con Co-Authored-By non-utente.
Rimuovi quella riga dal commit message e riprova.
EOF
  exit 2
fi

# Regola 2: git commit --no-verify
if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qE -- '--no-verify\b'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] git commit --no-verify
Motivo: skip degli hook senza approvazione esplicita dell'utente. Se gli hook stanno fallendo, investigare la causa.
EOF
  exit 2
fi

# Regola 3: git push --force su main/master
if echo "$command" | grep -qE 'git\s+push' && echo "$command" | grep -qE -- '(--force\b|-f\b|\+)' && echo "$command" | grep -qE '\b(main|master)\b'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] git push --force su main/master
Motivo: operazione distruttiva non reversibile su branch primario. Chiedi conferma esplicita all'utente.
EOF
  exit 2
fi

# Regola 4: --no-gpg-sign / --no-verify in altre forme
if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qE -- '--no-gpg-sign'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] --no-gpg-sign passato senza autorizzazione.
EOF
  exit 2
fi

exit 0
