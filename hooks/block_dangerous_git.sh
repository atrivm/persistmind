#!/usr/bin/env bash
# PreToolUse hook on Bash — blocks dangerous git operations.
# Receives a JSON {tool_name, tool_input.command, ...} on stdin.
# Exit 0 = allow. Exit !=0 + stderr = block with that message.

set -eu

# Read JSON from stdin
input=$(cat)

# Extract the command
command=$(echo "$input" | jq -r '.tool_input.command // ""')

# Skip immediately if it's not a git command
if ! echo "$command" | grep -qE '(^|[;&|]\s*)git\b'; then
  exit 0
fi

# Rule 1: git commit with Co-Authored-By
if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qi 'Co-Authored-By'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] git commit contains 'Co-Authored-By'.
Global memory: feedback_no_coauthored_by.md
Reason: Vercel Hobby and other CIs reject deploys with non-user Co-Authored-By trailers.
Remove that line from the commit message and retry.
EOF
  exit 2
fi

# Rule 2: git commit --no-verify
if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qE -- '--no-verify\b'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] git commit --no-verify
Reason: skipping hooks without explicit user approval is not allowed. If hooks are failing, investigate the cause.
EOF
  exit 2
fi

# Rule 3: git push --force on main/master
if echo "$command" | grep -qE 'git\s+push' && echo "$command" | grep -qE -- '(--force\b|-f\b|\+)' && echo "$command" | grep -qE '\b(main|master)\b'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] git push --force on main/master
Reason: irreversible destructive operation on a primary branch. Ask the user for explicit confirmation.
EOF
  exit 2
fi

# Rule 4: --no-gpg-sign / --no-verify in other forms
if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qE -- '--no-gpg-sign'; then
  cat >&2 <<'EOF'
[HOOK BLOCK] --no-gpg-sign passed without authorization.
EOF
  exit 2
fi

exit 0
