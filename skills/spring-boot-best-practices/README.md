# spring-boot-best-practices

Spring Boot 3 + Java 21 + MyBatis Plus 后端的编码规范，46 条规则分 8 类。

结构参考 [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices)。

## 为什么是这个结构

规范文档有两种给 agent 用的方式：

| | 路径注入（`.claude/rules` + `paths:`） | 渐进披露（本结构） |
|---|---|---|
| 加载 | 命中 glob 就自动注入全文 | agent 读索引，自己决定读哪条 |
| 粒度 | 一主题一大文件 | 一约定一小文件 |
| 失效模式 | glob 写错 → 要么永不命中，要么无差别命中 | 索引写差 → 挑不准该读哪条 |
| 可寻址 | 无 slug，没法引用单条 | 每条有稳定 slug，review 可点名 |

选后者的直接原因：前者的 glob 是个易错且沉默的机制。原始规则集里 11 个文件的 `paths:` 都带着规划工作流产物的通配，导致任何规划动作都无差别注入约 10.5 KB token；同时 React 规则的 `paths` 写的是 `**/*.vue` 而项目零个 `.vue`，那条规则从未命中过——两种失效都不报错，只能靠人工审计发现。

渐进披露没有这个机制，也就没有这类故障。

## 结构

```
SKILL.md            索引：46 条 slug + 一行摘要 + 按任务定位表（约 5 KB）
rules/
  _sections.md      分类定义：ID / 排序 / 影响级别 / 描述（编译输入）
  _template.md      单条规则骨架
  <prefix>-<slug>.md  规则正文，均值约 800 B
AGENTS.md           全量编译版（约 50 KB），由 scripts/build.sh 生成
scripts/build.sh    _sections.md + rules/*.md → AGENTS.md
metadata.json       版本、摘要、参考链接
```

## 影响级别

按**违反后果**划分，不按出现频率——这决定了 agent 在冲突时先服从哪条：

| 级别 | 含义 | 分类 |
|---|---|---|
| CRITICAL | 即 bug、安全问题，或直接跑不起来 | `layer-` `crypto-` `entity-` |
| HIGH | 能跑，但审查必打回、后续必返工 | `db-` `envelope-` `dto-` |
| MEDIUM | 不一致，但功能正确 | `naming-` |
| LOW | 风格偏好 | `stack-` |

## 新增一条规则

1. 拷 `rules/_template.md` 为 `rules/<prefix>-<slug>.md`，前缀取自 `_sections.md`
2. 写正文——**必须**含「为什么」和「违反的后果」，只写「应该这样」的规则 agent 遵守率低
3. 在 `SKILL.md` 对应分类下加一行索引，摘要写清触发条件
4. `bash scripts/build.sh` 重新编译 `AGENTS.md`
5. 校验索引与文件一一对应：

```bash
index_file="$(mktemp)"
rules_file="$(mktemp)"
trap 'rm -f "$index_file" "$rules_file"' EXIT
grep -oE '^- `[a-z]+-[a-z-]+`' SKILL.md | tr -d '`' | sed 's/^- //' | sort > "$index_file"
ls rules/[a-z]*.md | xargs -n1 basename | sed 's/\.md$//' | sort > "$rules_file"
diff "$index_file" "$rules_file" && echo OK
```

索引与文件不一致是本结构唯一的沉默故障：索引多写 → agent Read 失败；索引漏写 → 规则永远不被发现。每次改动后跑一遍。

## 启用

skill 需放在 Claude Code 能发现的位置：

```bash
# 全局启用（所有项目）
# 在仓库根目录执行
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/spring-boot-best-practices" \
      "$HOME/.claude/skills/spring-boot-best-practices"

# 或单项目启用
mkdir -p "<project>/.claude/skills"
ln -s "$(pwd)/skills/spring-boot-best-practices" \
      "<project>/.claude/skills/spring-boot-best-practices"
```

用符号链接而非拷贝，本仓才是唯一事实来源。

## 边界

本 skill 是**跨项目通用**规范。项目的包名、模块划分、数据库层数、锁定的业务决策以该项目 `CLAUDE.md` 为准，冲突时 CLAUDE.md 优先。

不要把规则内容复制进项目 `CLAUDE.md`——CLAUDE.md 每会话常驻，重复内容的成本按会话数累计，且两份副本必然漂移。
