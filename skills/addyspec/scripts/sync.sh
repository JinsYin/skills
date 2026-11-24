#!/usr/bin/env bash
# Re-vendor addyosmani/agent-skills commands + personas into addyspec.
# Usage: scripts/sync.sh [ref]   (default: main)
set -euo pipefail

ref="${1:-main}"
skill="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git clone -q https://github.com/addyosmani/agent-skills.git "$tmp/up"
git -C "$tmp/up" checkout -q "$ref"
sha="$(git -C "$tmp/up" rev-parse --short HEAD)"
date="$(git -C "$tmp/up" log -1 --format=%cs)"

list() { [ -d "$1" ] && ls "$1" | sed 's/\.md$//' | sort || true; }
old_cmds="$(list "$skill/references/commands")"
old_personas="$(list "$skill/references/personas")"

rm -rf "$skill/references/commands" "$skill/references/personas"
mkdir -p "$skill/references/commands" "$skill/references/personas"
cp "$tmp/up/.claude/commands/"*.md "$skill/references/commands/"
cp "$tmp/up/agents/"*.md "$skill/references/personas/"
cp "$tmp/up/LICENSE" "$skill/references/LICENSE"

sed -i.bak -E "s|^Snapshot: upstream \`[0-9a-f]+\` \([0-9-]+\)\.|Snapshot: upstream \`$sha\` ($date).|" "$skill/SKILL.md"
rm -f "$skill/SKILL.md.bak"
grep -q "^Snapshot: upstream \`$sha\`" "$skill/SKILL.md" || { echo "Snapshot line not updated in SKILL.md" >&2; exit 1; }

report() { # $1 label, $2 old list, $3 dir
  local new; new="$(list "$3")"
  local added removed
  added="$(comm -13 <(echo "$2") <(echo "$new") | xargs)"
  removed="$(comm -23 <(echo "$2") <(echo "$new") | xargs)"
  echo "$1 added: ${added:-none}"
  echo "$1 removed: ${removed:-none}"
}

echo "Snapshot: $sha ($date)"
report "Commands" "$old_cmds" "$skill/references/commands"
report "Personas" "$old_personas" "$skill/references/personas"
echo "agent-skills refs per command:"
for f in "$skill/references/commands/"*.md; do
  refs="$(grep -o 'agent-skills:[a-z-]*' "$f" | sed 's/agent-skills://' | sort -u | xargs || true)"
  echo "  $(basename "$f" .md): ${refs:-none}"
done
