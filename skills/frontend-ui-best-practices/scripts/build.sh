#!/usr/bin/env bash
# 从 rules/_sections.md + rules/*.md 编译出 AGENTS.md 全量版。
# 标题取自 SKILL.md 的首个 H1，故本脚本可在各 skill 间通用。
# 用法：bash scripts/build.sh
# 兼容 bash 3.2（macOS 自带），不使用 mapfile / readarray。
set -euo pipefail

cd "$(dirname "$0")/.."
OUT=AGENTS.md
RULES=rules

TITLE=$(grep -m1 '^# ' SKILL.md | sed 's/^# //')
[ -z "$TITLE" ] && { echo "❌ SKILL.md 中找不到 H1 标题"; exit 1; }

{
  echo "# $TITLE"
  echo
  echo "> 本文件由 \`scripts/build.sh\` 从 \`rules/\` 自动生成，请勿手工编辑。"
  echo "> 生成时间：$(date '+%Y-%m-%d %H:%M:%S')"
  echo
} > "$OUT"

total=0
# 分类顺序与标题从 _sections.md 解析：'## N. 标题 (prefix)'
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
    # 剥掉 frontmatter（前两个 --- 之间），正文 H2 降为 H3
    awk 'BEGIN{n=0} /^---$/{n++; next} n>=2' "$f" \
      | sed -E 's/^## /### /' >> "$OUT"
    printf '\n' >> "$OUT"
    total=$((total + 1))
  done
done < <(grep -E '^## [0-9]+\. .+ \(.+\)$' "$RULES/_sections.md")

echo "✅ $OUT 已生成：$total 条规则，$(wc -c < "$OUT") 字节"
