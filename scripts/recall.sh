#!/usr/bin/env bash
# Word search across the memory layers of the active account: the global layer
# (~/.claude/memory), every project memory and the observation buffer, plus any
# extra folder given as an argument. Files with the most matching lines first:
#   <matching lines><TAB><path><TAB><description>
# Usage: recall.sh '<extended regex>' [extra-dir ...]
# Example: recall.sh 'proiettor|projector|epson'

pattern="${1:-}"
if [ -z "$pattern" ]; then
  echo "usage: recall.sh '<extended regex>' [extra-dir ...]" >&2
  exit 2
fi
shift

claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
obs_dir="${PM_OBSERVATIONS_ROOT:-$claude_dir/observations}"
obs_dir="${obs_dir/#\~/$HOME}"
set -- "$HOME/.claude/memory" "$obs_dir"/* "$claude_dir"/projects/*/memory "$@"

# Resolve each root to its real path: BSD grep -R does not follow symlinks, and
# a folder shared between accounts is a symlink (one root per observation folder).
roots=()
for dir in "$@"; do
  [ -d "$dir" ] && roots+=("$(cd "$dir" && pwd -P)")
done
[ ${#roots[@]} -eq 0 ] && exit 0

tab="$(printf '\t')"
grep -R -c -i -E --include='*.md' -- "$pattern" "${roots[@]}" 2>/dev/null \
  | awk '{ n = $0; sub(/.*:/, "", n); f = $0; sub(/:[0-9]+$/, "", f); if (n > 0) print n "\t" f }' \
  | sort -t "$tab" -k1,1nr \
  | head -n "${PM_RECALL_LIMIT:-15}" \
  | while IFS="$tab" read -r count file; do
      desc=$(grep -m1 '^description:' "$file" | cut -c14- | cut -c1-160)
      printf '%s\t%s\t%s\n' "$count" "$file" "$desc"
    done
