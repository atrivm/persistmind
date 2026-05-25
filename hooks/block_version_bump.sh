#!/usr/bin/env bash
# PreToolUse hook on Edit/Write — blocca version bump in file di configurazione.
# Riceve JSON {tool_name, tool_input.file_path, tool_input.old_string, tool_input.new_string, tool_input.content, ...}

set -eu

input=$(cat)
tool=$(echo "$input" | jq -r '.tool_name // ""')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Lista di file in cui il campo "version" è tipicamente quello di release
case "$(basename "$file_path")" in
  package.json|pubspec.yaml|pubspec.yml|Cargo.toml|pyproject.toml|setup.py|setup.cfg|composer.json|gemspec)
    is_config_file=1
    ;;
  *)
    is_config_file=0
    ;;
esac

if [ "$is_config_file" -ne 1 ]; then
  exit 0
fi

# Se Edit: confronta old_string vs new_string per la riga version
if [ "$tool" = "Edit" ]; then
  old=$(echo "$input" | jq -r '.tool_input.old_string // ""')
  new=$(echo "$input" | jq -r '.tool_input.new_string // ""')

  # Estrai il valore di "version" da entrambi (pattern: version: "x.y.z" o "version": "x.y.z" o version = "x.y.z")
  old_ver=$(echo "$old" | grep -oE '("?version"?\s*[:=]\s*"[^"]+")' | head -1 || true)
  new_ver=$(echo "$new" | grep -oE '("?version"?\s*[:=]\s*"[^"]+")' | head -1 || true)

  if [ -n "$old_ver" ] && [ -n "$new_ver" ] && [ "$old_ver" != "$new_ver" ]; then
    cat >&2 <<EOF
[HOOK BLOCK] Version bump rilevato in $(basename "$file_path"):
  Da: $old_ver
  A:  $new_ver
Memoria globale: feedback_no_version_bump.md
Motivo: il version bump è un atto deliberato di release. Se davvero vuoi bumparla, chiedi conferma esplicita all'utente prima di procedere.
EOF
    exit 2
  fi
fi

# Per Write (full overwrite): warning ma non blocco hard, perché Write è spesso usato per nuovi file
if [ "$tool" = "Write" ] && [ -f "$file_path" ]; then
  content=$(echo "$input" | jq -r '.tool_input.content // ""')
  new_ver=$(echo "$content" | grep -oE '("?version"?\s*[:=]\s*"[^"]+")' | head -1 || true)
  existing_ver=$(grep -oE '("?version"?\s*[:=]\s*"[^"]+")' "$file_path" | head -1 || true)

  if [ -n "$new_ver" ] && [ -n "$existing_ver" ] && [ "$new_ver" != "$existing_ver" ]; then
    cat >&2 <<EOF
[HOOK BLOCK] Write su $(basename "$file_path") sostituirebbe version:
  Esistente: $existing_ver
  Nuova:     $new_ver
Memoria globale: feedback_no_version_bump.md
Usa Edit chirurgico, e bumpa solo se l'utente l'ha richiesto.
EOF
    exit 2
  fi
fi

exit 0
