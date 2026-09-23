#!/usr/bin/env bash
# 视觉冻结检查：plan 车道只换数据实现、接线、加守卫，不得改 token、class、布局、文案。
# 用法：scripts/visual-freeze.sh [base]；base 缺省为当前分支与 main/master 的分叉点。
set -euo pipefail
cd "$(dirname "$0")/.."
trunk=$(git rev-parse -q --verify main >/dev/null && echo main || echo master)
base=${1:-$(git merge-base HEAD "$trunk")}
fail=0

# 1. token、样式、组件库原语与 products/ 设计输入整体冻结（含未跟踪的新文件）
frozen=$( { git diff --name-only "$base" -- src/styles src/components/ui 'tailwind.config.*' components.json ':/products'
            git ls-files --others --exclude-standard -- src/styles src/components/ui; } | sort -u)
[ -n "$frozen" ] && { printf '✗ 冻结路径被改动：\n%s\n' "$frozen"; fail=1; }

# 2. 视觉指纹：按出现顺序抽取 className / variant / size / style 属性、cva( / cn( 调用与非 ASCII 文案；
#    注释、空白、换行不计，所以接线、改 handler、加 disabled、条件包裹都不会改变指纹
fp() {
  perl -0777 -ne '
    s{/\*.*?\*/}{}gs; s{(?<![:\w"\x27])//[^\n]*}{}g;
    my $br = qr/(\{(?:[^{}]++|(?-1))*\})/; my $pa = qr/(\((?:[^()]++|(?-1))*\))/;
    while (/\b(?:className|variant|size|style)=(?:"[^"]*"|\x27[^\x27]*\x27|$br)|\b(?:cva|cn)$pa|[\x80-\xff]+/g) {
      (my $m = $&) =~ s/\s+/ /g; print "$m\n";
    }'
}
scope=(-- 'src/*.ts' 'src/*.tsx' ':!src/mocks' ':!src/styles' ':!src/components/ui' ':!*.test.*' ':!*.spec.*' ':!*__tests__*')
while IFS=$'\t' read -r st a b; do
  case $st in
    D)  old=$(git show "$base:./$a" | fp); new=''; f=$a ;;
    A)  old=''; new=$(fp < "$a"); f=$a ;;
    R*) old=$(git show "$base:./$a" | fp); new=$(fp < "$b"); f=$b ;;
    *)  old=$(git show "$base:./$a" | fp); new=$(fp < "$a"); f=$a ;;
  esac
  if [ "$old" != "$new" ]; then
    echo "✗ 视觉指纹变化：$f"; diff <(printf '%s\n' "$old") <(printf '%s\n' "$new") | sed 's/^/    /' || true; fail=1
  fi
done < <( git diff --name-status -M --relative "$base" "${scope[@]}"
          git ls-files --others --exclude-standard "${scope[@]}" | awk '{print "A\t" $0}' )

[ $fail -eq 0 ] && echo "✓ 视觉层未改动（基线 ${base:0:7}）"
exit $fail
