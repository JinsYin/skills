# frontend-ui-best-practices

React + shadcn/ui 后台管理系统的界面与交互规范，16 条规则分 6 类。

与 [`spring-boot-best-practices`](../spring-boot-best-practices/) 同构，结构参考
[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices)：
`SKILL.md` 只做索引，规则正文一条一文件按需读取，`scripts/build.sh` 编译出全量版 `AGENTS.md`。

## 影响级别

后端规范按「违反即 bug / 跑不起来」定级，前端不适用同一把尺——界面问题很少让程序崩溃，
但会让用户做错事。所以这里按**用户后果**定级：

| 级别 | 含义 | 分类 |
|---|---|---|
| CRITICAL | 数据丢失或不可恢复的误操作 | `overlay-` |
| HIGH | 用户无法完成任务，或被明确误导 | `form-` `list-` |
| MEDIUM | 能完成但体验受损 | `format-` |
| LOW | 观感不一致 | `consistency-` `stack-` |

弹层排在最高优先级不是因为它最常写，而是因为**缺确认框的删除**和**关闭后不重置的表单**
这两类问题直接造成不可恢复的数据后果，且都难以在手工测试中复现。

## 来源与取舍

内容源自一份 49 行的 `uiux.md`。转换时做了三件事：

1. **拆成原子规则**，每条补上「为什么」与「违反后果」——原文多为祈使句清单
   （"必须 X"、"不要 Y"），没有成因说明，agent 遵守率低。
2. **剔除组织专属项**。以下不属于通用规范，应放在各项目自己的 `CLAUDE.md`：
   - 平台中文名与内部代号的对应关系
   - 邮箱域名
   - logo 规格（如 32x32）与顶栏构成
   - 「控制台构建为单 HTML 页 + 锚点分节」这类特定架构约定
3. **保留待落实项**。原文有 5 条带 `[ ]` 前缀（密码眼睛图标、抽屉/弹窗遮罩一致、
   弹层尺寸一致、关闭后重置表单、同功能图标一致）。措辞均为 must，按规则收录；
   `[ ]` 记录的是**代码合规状态**而非规则效力，那属于项目的技术债清单，不属于规则库。

## 新增一条规则

见 [`spring-boot-best-practices/README.md`](../spring-boot-best-practices/README.md#新增一条规则)，流程一致。
`scripts/build.sh` 两个 skill 通用——标题从 `SKILL.md` 的 H1 自动读取，不需按 skill 改脚本。

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
