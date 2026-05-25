#!/usr/bin/env bash
# PreToolUse hook on Edit/Write — blocks version bumps in configuration files.
# Receives a JSON {tool_name, tool_input.file_path, tool_input.old_string, tool_input.new_string, tool_input.content, ...}

set -eu

input=$(cat)
tool=$(echo "$input" | jq -r '.tool_name // ""')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# List of files where the "version" field typically denotes a release
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

# If Edit: compare old_string vs new_string for the version line
if [ "$tool" = "Edit" ]; then
  old=$(echo "$input" | jq -r '.tool_input.old_string // ""')
  new=$(echo "$input" | jq -r '.tool_input.new_string // ""')

  # Extract the "version" value from both (patterns: version: "x.y.z" or "version": "x.y.z" or version = "x.y.z")
  old_ver=$(echo "$old" | grep -oE '("?version"?\s*[:=]\s*"[^"]+")' | head -1 || true)
  new_ver=$(echo "$new" | grep -oE '("?version"?\s*[:=]\s*"[^"]+")' | head -1 || true)

  if [ -n "$old_ver" ] && [ -n "$new_ver" ] && [ "$old_ver" != "$new_ver" ]; then
    cat >&2 <<EOF
[HOOK BLOCK] Version bump detected in $(basename "$file_path"):
  From: $old_ver
  To:   $new_ver
Global memory: feedback_no_version_bump.md
Reason: a version bump is a deliberate release action. If you really want to bump it, ask the user for explicit confirmation first.
EOF
    exit 2
  fi
fi

# For Write (full overwrite): warning but not a hard block, since Write is often used for new files
if [ "$tool" = "Write" ] && [ -f "$file_path" ]; then
  content=$(echo "$input" | jq -r '.tool_input.content // ""')
  new_ver=$(echo "$content" | grep -oE '("?version"?\s*[:=]\s*"[^"]+")' | head -1 || true)
  existing_ver=$(grep -oE '("?version"?\s*[:=]\s*"[^"]+")' "$file_path" | head -1 || true)

  if [ -n "$new_ver" ] && [ -n "$existing_ver" ] && [ "$new_ver" != "$existing_ver" ]; then
    cat >&2 <<EOF
[HOOK BLOCK] Write to $(basename "$file_path") would replace the version field:
  Existing: $existing_ver
  New:      $new_ver
Global memory: feedback_no_version_bump.md
Use a surgical Edit, and only bump if the user has explicitly requested it.
EOF
    exit 2
  fi
fi

exit 0
