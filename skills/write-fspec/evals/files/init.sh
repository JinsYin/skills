#!/bin/sh
# 用 steps/NN-<slug>/ 叠加目录为 fixture 副本构建 git 历史，最后删除 steps/。
# slug 为英文 kebab-case，去掉序号、连字符换成空格后作为提交信息。
# 用法：cp -R files/<fixture> <tmp> && sh files/init.sh <tmp>
set -eu
cd "$1"
git init -q
echo 'steps/' >> .git/info/exclude
n=0
for s in steps/*/; do
  n=$((n + 1))
  cp -R "${s}." .
  git add -A
  # 固定作者与时间，保证 commit 可复现
  GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.com \
  GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.com \
  GIT_AUTHOR_DATE="2026-10-0${n}T10:00:00+08:00" GIT_COMMITTER_DATE="2026-10-0${n}T10:00:00+08:00" \
    git commit -q -m "$(basename "${s}" | sed 's/^[0-9]*-//; s/-/ /g')"
done
rm -rf steps
