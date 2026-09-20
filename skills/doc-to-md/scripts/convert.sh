#!/usr/bin/env bash
#
# doc-to-md: 用 markitdown 把文档转成 Markdown，再用 markdownlint-cli2 --fix 清理排版，
#        最后写到与源文件同目录、同主名、扩展名为 .md 的文件。
#
# 用法:
#   convert.sh [--force] [--no-lint] <文件或目录> [更多文件或目录...]
#   convert.sh --lint-only <file.md> [更多 .md / 目录...]
#
#   --force      目标 .md 已存在时直接覆盖（默认：拒绝覆盖并以退出码 3 报告，
#                交给调用方先征求用户同意）
#   --no-lint    只转换不做 lint（极少用；默认会跑宽松规则的 --fix）
#   --lint-only  跳过转换，只对传入的 .md 重跑一遍 markdownlint --fix。
#                供 LLM 精修阶段手动 Edit 之后做排版收尾用（见 SKILL.md）。
#
# 退出码:
#   0  全部成功（lint 残留告警不算失败，会原样打印）
#   2  markitdown 转换失败
#   3  目标已存在且未带 --force（需要先问用户）
#   4  没有可处理的输入
#
# 设计说明：转换 + lint 是确定性步骤，固化在脚本里，避免每次调用都重写一遍。
# “是否覆盖”“LLM 精修”这类需要人判断 / 需要智能的环节留在脚本外（SKILL.md 指挥 Claude）。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINT_CONFIG="${SCRIPT_DIR}/../assets/markdownlint.jsonc"

FORCE=0
DO_LINT=1
LINT_ONLY=0
INPUTS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)     FORCE=1; shift ;;
    --no-lint)   DO_LINT=0; shift ;;
    --lint-only) LINT_ONLY=1; shift ;;
    --) shift; while [[ $# -gt 0 ]]; do INPUTS+=("$1"); shift; done ;;
    *) INPUTS+=("$1"); shift ;;
  esac
done

# markdownlint-cli2 把位置参数当作 glob，文件名里的 ( ) [ ] { } * ? ! 会被当通配符，
# 命中不到文件就静默「Linting: 0 file(s)」漏 lint（中文文档名常含 () ）。把这些元字符
# 转义成字面量后再传，micromatch 会按字面匹配到真实文件。
glob_escape() {
  # 在 ] [ ( ) { } * ? ! | + @ ^ $ 前加反斜杠（] 放类首才算字面量）。
  printf '%s' "$1" | sed 's/[][(){}*?!|+@^$]/\\&/g'
}

# 对传入的 .md 列表跑一遍宽松规则的 --fix（残留告警只打印，不算失败）。
run_lint() {
  if ! command -v npx >/dev/null 2>&1; then
    echo "⚠️  未找到 npx，跳过 lint。源转换结果已保存。" >&2
    return
  fi
  echo "🧹 markdownlint --fix（宽松规则）..."
  local globs=() f
  for f in "$@"; do globs+=("$(glob_escape "$f")"); done
  npx --yes markdownlint-cli2 --fix --config "$LINT_CONFIG" "${globs[@]}" || true
}

# ── --lint-only：只对已有 .md 收尾，不转换 ────────────────────────────
# LLM 精修会用 Edit 直接改 .md，改完需要把缩进/空行/行尾空格这类排版重新规整，
# 但绝不能重新跑 markitdown（那会用原始产物覆盖掉精修成果）。所以单独走这条路。
if [[ $LINT_ONLY -eq 1 ]]; then
  MD_FILES=()
  for item in "${INPUTS[@]:-}"; do
    [[ -z "$item" ]] && continue
    if [[ -d "$item" ]]; then
      while IFS= read -r f; do MD_FILES+=("$f"); done \
        < <(find "$item" -maxdepth 1 -type f -name '*.md' | sort)
    elif [[ -f "$item" && "${item##*.}" == "md" ]]; then
      MD_FILES+=("$item")
    else
      echo "⚠️  跳过（非 .md 或不存在）：$item" >&2
    fi
  done
  if [[ ${#MD_FILES[@]} -eq 0 ]]; then
    echo "❌ 没有可 lint 的 .md 文件。" >&2
    exit 4
  fi
  run_lint "${MD_FILES[@]}"
  echo "✅ lint 收尾完成："
  for f in "${MD_FILES[@]}"; do echo "   $f"; done
  exit 0
fi

# markitdown 支持的输入扩展名（用于展开目录时筛选）。
SUPPORTED_EXT="pdf docx pptx xlsx xls html htm csv json xml epub msg zip rtf odt md txt png jpg jpeg gif bmp tiff webp mp3 wav m4a"

is_supported() {
  local ext="${1##*.}"
  ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  for e in $SUPPORTED_EXT; do [[ "$ext" == "$e" ]] && return 0; done
  return 1
}

# 把目录展开成其下受支持的文件；普通文件原样保留。
FILES=()
for item in "${INPUTS[@]:-}"; do
  [[ -z "$item" ]] && continue
  if [[ -d "$item" ]]; then
    while IFS= read -r f; do
      is_supported "$f" && FILES+=("$f")
    done < <(find "$item" -maxdepth 1 -type f | sort)
  elif [[ -f "$item" ]]; then
    FILES+=("$item")
  else
    echo "⚠️  跳过：找不到 $item" >&2
  fi
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "❌ 没有可处理的输入文件。" >&2
  exit 4
fi

EXIT=0
CONVERTED=()

for src in "${FILES[@]}"; do
  ext="${src##*.}"
  ext_lc="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"

  # 源文件本身就是 .md，没必要再转，避免自我覆盖。
  if [[ "$ext_lc" == "md" ]]; then
    echo "ℹ️  跳过（已是 Markdown）：$src" >&2
    continue
  fi

  out="${src%.*}.md"

  if [[ -e "$out" && $FORCE -ne 1 ]]; then
    echo "EXISTS	$out" >&2
    echo "⚠️  目标已存在：$out —— 需要确认后用 --force 覆盖。" >&2
    EXIT=3
    continue
  fi

  echo "▶️  转换：$src → $out"
  if ! markitdown "$src" -o "$out"; then
    echo "❌ markitdown 转换失败：$src" >&2
    rm -f "$out" 2>/dev/null
    EXIT=2
    continue
  fi

  # 语义级清理（目录→列表 / 裸 JSON→```json 围栏 / 删空表格行）。
  # 纯 Python、无外部依赖，属于产出质量的一部分，始终执行。
  if command -v python3 >/dev/null 2>&1; then
    python3 "${SCRIPT_DIR}/postprocess.py" "$out" || \
      echo "⚠️  postprocess 异常（已保留转换结果）：$out" >&2
  else
    echo "⚠️  未找到 python3，跳过语义清理。" >&2
  fi

  CONVERTED+=("$out")
done

# lint 阶段：对本次成功转换的文件统一跑一次 --fix（残留告警只打印，不算失败）。
if [[ $DO_LINT -eq 1 && ${#CONVERTED[@]} -gt 0 ]]; then
  run_lint "${CONVERTED[@]}"
fi

if [[ ${#CONVERTED[@]} -gt 0 ]]; then
  echo "✅ 已生成（确定性管线完成；下一步按 SKILL.md 做 LLM 精修）："
  for f in "${CONVERTED[@]}"; do echo "   $f"; done
fi

exit $EXIT
