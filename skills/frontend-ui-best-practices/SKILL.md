---
name: frontend-ui-best-practices
description: React + shadcn/ui 后台管理系统的界面与交互规范。涵盖表单校验时机与错误呈现、弹窗抽屉的状态重置与破坏性操作确认、列表分页与表格对齐、日期数字格式、图标与提示的一致性、模块 README 文档要求。在编写、审查或重构前端页面时使用——尤其是做表单、列表页、弹窗抽屉、删除等破坏性操作、或调整界面文案与格式时。
license: MIT
metadata:
  author: JinsYin
  version: "1.0.0"
---

# Frontend UI Best Practices

React + shadcn/ui 后台管理系统的界面规范，17 条规则分 6 类，按**违反给用户造成的后果**排序。

## 如何使用本 skill

**不要一次读完所有规则。** 先在下面的索引里定位与当前任务相关的条目，再按需 `Read` 对应文件：

```
rules/form-validation-timing.md
rules/overlay-reset-on-close.md
```

每条规则含：为什么、错误示例、正确示例。

| 你在做什么 | 先读 |
|---|---|
| 做表单（新建/编辑） | `form-*`、`overlay-reset-on-close` |
| 做列表页 | `list-*`、`format-date-number` |
| 做弹窗 / 抽屉 | `overlay-*` |
| 做删除等破坏性操作 | `overlay-confirm-destructive` |
| 调文案与格式 | `format-*` |
| 加图标或提示 | `consistency-*` |
| 新增子包 / 写模块文档 | `stack-module-readme` |
| 界面走查 / 审查 | 按改动涉及的组件类型选对应分类 |

## 分类与影响级别

影响级别按**用户后果**划分：CRITICAL = 数据丢失或不可恢复的误操作；HIGH = 用户无法完成任务或被明确误导；MEDIUM = 能完成但体验受损；LOW = 观感不一致。

| 优先级 | 分类 | 影响 | 前缀 | 条数 |
|---|---|---|---|---|
| 1 | 弹层与破坏性操作 | CRITICAL | `overlay-` | 3 |
| 2 | 表单 | HIGH | `form-` | 4 |
| 3 | 列表与表格 | HIGH | `list-` | 3 |
| 4 | 格式与文案 | MEDIUM | `format-` | 2 |
| 5 | 视觉一致性 | LOW | `consistency-` | 3 |
| 6 | 技术栈基线 | LOW | `stack-` | 2 |

## 规则索引

### 1. 弹层与破坏性操作 (CRITICAL)

- `overlay-confirm-destructive` — 删除类操作用自定义确认弹窗，禁用原生 `confirm`，说清对象与后果
- `overlay-reset-on-close` — 弹层关闭后必须重置表单值与校验错误，否则脏状态会被误提交
- `overlay-consistent-size` — 同资源的新建/编辑/查看弹层尺寸一致，抽屉与弹窗遮罩一致

### 2. 表单 (HIGH)

- `form-validation-timing` — blur 首验、出错后转 change 复验、submit 兜底
- `form-error-display` — 错误三件套：边框变色 + 字段下方具体文案 + 输入时实时清除
- `form-disable-autofill` — 关自动填充，密码框须用 `new-password`（`off` 对密码无效）
- `form-readonly-styling` — 不可编辑时灰化文字而非输入框，悬停 `not-allowed`

### 3. 列表与表格 (HIGH)

- `list-windowed-pagination` — 页码必须开窗，全量渲染在大数据量下卡死页面
- `list-table-alignment` — 表头与单元格一律左对齐，空值显示 `-`
- `list-toolbar-order` — 工具栏顺序：搜索 → 筛选 → 图标刷新；行内操作风格统一

### 4. 格式与文案 (MEDIUM)

- `format-date-number` — 日期 `YYYY-MM-DD`，数字不加千分位逗号
- `format-language-naming` — 界面默认中文，不暴露内部项目代号

### 5. 视觉一致性 (LOW)

- `consistency-toast` — Toast 须图标 + 文字，图标按级别变色，错误须给具体原因
- `consistency-icons` — 同功能全站同图标，集中导出而非各页自选
- `consistency-page-chrome` — favicon / logo / 总条数 / 必填标记 / 可搜索下拉

### 6. 技术栈基线 (LOW)

- `stack-baseline` — pnpm + Vite + React + TS + shadcn/ui + Tailwind
- `stack-module-readme` — 根目录必有 README；monorepo 下每个子包也各有一份，单包只需根 README

## 与项目 CLAUDE.md 的关系

本 skill 是**跨项目通用**规范。凡涉及具体组织或项目的内容——平台中文名、邮箱域名、logo 规格、顶栏构成、目录结构、路由划分——一律以该项目的 `CLAUDE.md` 为准，冲突时 CLAUDE.md 优先。

不要把这里的内容复制进项目的 `CLAUDE.md`：CLAUDE.md 每会话常驻，重复内容的成本按会话数累计，且两份副本必然漂移。

## 全量编译版

需要一次性获取全部规则时读 `AGENTS.md`。该文件由 `scripts/build.sh` 从 `rules/` 生成，**不要手工编辑**。
