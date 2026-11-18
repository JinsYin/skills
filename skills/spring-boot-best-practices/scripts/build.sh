#!/usr/bin/env bash
# Compile the full AGENTS.md from rules/_sections.md + rules/*.md.
# The title is taken from the first H1 of SKILL.md, so this script is skill-agnostic.
# Usage: bash scripts/build.sh
# Compatible with bash 3.2 (shipped with macOS): no mapfile / readarray.
set -euo pipefail

cd "$(dirname "$0")/.."
OUT=AGENTS.md
RULES=rules

TITLE=$(grep -m1 '^# ' SKILL.md | sed 's/^# //')
[ -z "$TITLE" ] && { echo "❌ No H1 title found in SKILL.md"; exit 1; }

{
  echo "# $TITLE"
  echo
  echo "> Generated from \`rules/\` by \`scripts/build.sh\`. Do not edit by hand."
  echo "> Generated at: $(date '+%Y-%m-%d %H:%M:%S')"
  echo
} > "$OUT"

total=0
# Category order and titles are parsed from _sections.md: '## N. Title (prefix)'
while IFS= read -r line; do
  [ -z "$line" ] && continue
  num=$(echo "$line"   | sed -E 's/^## ([0-9]+)\..*$/\1/')
  title=$(echo "$line" | sed -E 's/^## [0-9]+\. (.+) \(.+\)$/\1/')
  prefix=$(echo "$line"| sed -E 's/^.*\((.+)\)$/\1/')

  set +e
  files=$(ls "$RULES/${prefix}-"*.md 2>/dev/null)
  set -e
  [ -z "$files" ] && continue

  printf '## %s. %s\n\n' "$num" "$title" >> "$OUT"

  for f in $files; do
    # Strip the frontmatter (between the first two ---) and demote body H2 to H3
    awk 'BEGIN{n=0} /^---$/{n++; next} n>=2' "$f" \
      | sed -E 's/^## /### /' >> "$OUT"
    printf '\n' >> "$OUT"
    total=$((total + 1))
  done
done < <(grep -E '^## [0-9]+\. .+ \(.+\)$' "$RULES/_sections.md")

echo "✅ $OUT written: $total rules, $(wc -c < "$OUT") bytes"
