# frontend-ui-best-practices

React + shadcn/ui 前端工程的技术栈基线与模块文档规范，2 条规则。

`SKILL.md` 只做索引，规则一条一文件按需读取，`scripts/build.sh` 编译出全量版 `AGENTS.md`。

## 范围

只覆盖**工程层**：依赖选型、项目结构、模块 README。界面与交互层（表单、弹层、列表、格式、
图标）属于 `ui-ux-best-practices`，两者不重叠，避免同一条规则存在两份必然漂移的副本。

## 新增一条规则

1. 复制 `rules/_template.md` 为 `rules/<前缀>-<名称>.md`
2. 在 `SKILL.md` 的规则索引里加一行
3. 新增分类时同步改 `rules/_sections.md`
4. 重新编译：`bash scripts/build.sh`

改完务必校验索引与文件一一对应，这是本结构唯一的沉默故障：

```bash
index_file="$(mktemp)"
rules_file="$(mktemp)"
trap 'rm -f "$index_file" "$rules_file"' EXIT
grep -oE '^- `[a-z]+-[a-z-]+`' SKILL.md | tr -d '`' | sed 's/^- //' | sort > "$index_file"
ls rules/[a-z]*.md | xargs -n1 basename | sed 's/\.md$//' | sort > "$rules_file"
diff "$index_file" "$rules_file" && echo OK
```

## 启用

```bash
# 在仓库根目录执行
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/frontend-ui-best-practices" \
      "$HOME/.claude/skills/frontend-ui-best-practices"
```

用符号链接而非拷贝，本仓才是唯一事实来源。
