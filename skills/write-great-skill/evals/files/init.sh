#!/usr/bin/env bash
# 用法：init.sh <scenario> <dest>
# 在 <dest>/project 构建 fixture 仓库（已提交、origin 指向本地 bare 仓库 <dest>/origin.git）。
# scenario：base | since-draft（base 之上叠加未提交的 --since 草稿，模拟第 1 步已完成）
set -euo pipefail
scenario="$1"; dest="$2"
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "${dest}"
cp -R "${here}/skills-repo" "${dest}/project"
git -C "${dest}" init -q --bare origin.git
cd "${dest}/project"
git init -q -b master
git config user.name eval; git config user.email eval@example.com
git add -A && git commit -qm "chore: 初始化" 
git remote add origin "${dest}/origin.git"
git push -q origin master
case "${scenario}" in
  base) ;;
  since-draft) cp -R "${here}/overlays/since-draft/." . ;;
  *) echo "unknown scenario: ${scenario}" >&2; exit 1 ;;
esac
