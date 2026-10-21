---
name: doc-writing-best-practices
description: 中文技术文档的写作规范。涵盖中西文混排的空格与标点、标题层级与代码块标注、表格与列表的取舍、以及"写清为什么"和"示例可直接抄用"的内容要求。在编写或修改 README、设计文档、运维手册、变更说明、注释块等任何面向人阅读的中文技术文档时使用——尤其是产出 Markdown 文件、写提交说明、或整理已有文档时。
license: MIT
metadata:
  author: JinsYin
  version: "1.0.0"
---

# Doc Writing Best Practices

中文技术文档的规范集，9 条规则分 3 类。

## 如何使用本 skill

规则总量小，可以先读索引再按需取；若正在集中整理一批文档，直接通读 `AGENTS.md` 也不贵。

| 你在做什么 | 先读 |
|---|---|
| 写任何中文文档 | `cjk-*`（3 条，成本最低收益最直接） |
| 写 README / 设计文档 | `content-*`、`struct-heading-no-skip`；链接多时 `struct-reference-links` |
| 写运维手册 / 操作步骤 | `content-example-copy-ready`、`struct-code-fence-language` |
| 整理已有文档 | 全部 |

## 这类规范的共性

文档的失效方式和代码不同：**没有编译器会告诉你写错了**。排版不一致、示例抄不动、缺少"为什么"——这些都不会报错，只会让读者慢慢地不再信任这份文档。

而一份过期或含糊的文档比没有文档更糟：它会被信任，然后把人带偏。

## 分类与影响级别

| 优先级 | 分类 | 影响 | 前缀 | 条数 |
|---|---|---|---|---|
| 1 | 内容质量 | HIGH | `content-` | 2 |
| 2 | 文档结构 | MEDIUM | `struct-` | 4 |
| 3 | 中文排版 | MEDIUM | `cjk-` | 3 |

排序按影响，不按阅读顺序——`cjk-*` 最常用但后果最轻。

## 规则索引

### 1. 内容质量（HIGH）

- `content-example-copy-ready` — 示例用真实值、可直接粘贴执行；占位符会被抄错，且错在读者的环境里
- `content-why-not-just-what` — 写清为什么，只写"怎么做"的文档在情况变化时无法判断是否还适用

### 2. 文档结构（MEDIUM）

- `struct-code-fence-language` — 代码块必须标语言；标错比不标更糟，纯输出显式标 `text`
- `struct-heading-no-skip` — 层级不跳级、一篇一个 H1、深度控制在 H4 内
- `struct-reference-links` — 链接超过约 5 个或有重复目标时用参考链接，定义集中文末分组
- `struct-table-vs-list` — 有共同维度用表格、无共同维度用列表；表格里不放长段落

### 3. 中文排版（MEDIUM）

- `cjk-latin-spacing` — 中文与西文、行内代码之间加空格；一致性比选哪一种更重要
- `cjk-number-spacing` — 中文与数字之间加空格
- `cjk-punctuation` — 中文句子用全角标点；判据是这一段的主语言，不是整篇文档

## 与项目规范的关系

本 skill 是**跨项目通用基线**。具体的术语表、平台称谓、对外文案口径属于项目事实，应写在项目的 `CLAUDE.md`，不要写进这里。

冲突时以项目自身的约定为准。

## 维护

改动 `rules/` 后必须重新生成全量版：

```bash
bash scripts/build.sh
```
