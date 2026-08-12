# 规则写法

分诊定了「放哪」，这份定「怎么写」。`spec-setup` 与 `spec-triage` 共用。

## 核心：写「为什么」和「后果」

只写「应该这样」的规则，agent 遵守率显著低——因为没有判断依据，遇到边界情形时无从推断该不该适用。

**弱：**

> 主键必须用 `IdType.ASSIGN_ID`。

**强：**

> `IdType.AUTO` 依赖数据库端自增列。目标库不是 MySQL 时（openGauss 的 `BIGSERIAL` 与 `AUTO_INCREMENT` 语义不等价），应用层不填 ID，INSERT 撞上 NOT NULL 直接失败——而报错指向字段约束，与真正的根因（主键策略）相距很远，排查代价高。

后者让 agent 能自己判断：遇到只跑 MySQL 的项目时这条要不要坚持，遇到类似的"应用层 vs 数据库端生成"问题时怎么类推。

## 单条规则的骨架

```markdown
---
title: 规则标题
impact: CRITICAL | HIGH | MEDIUM | LOW
impactDescription: 可选，违反的具体后果（如"INSERT 直接失败"）
tags: 逗号分隔
---

## 规则标题

一到三句：规则内容 + 为什么 + 违反后果。

**错误（说明错在哪）：**

```语言
反例
```

**正确（说明为什么对）：**

```语言
正例
```

可选：例外情形、补充说明、参考链接。
```

## 影响级别

按**违反后果**定级，不按出现频率。同一把尺不适用于所有领域——先定义本 skill 的尺子：

| 领域 | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|
| 后端 | 即 bug / 安全问题 / 跑不起来 | 审查必打回、必返工 | 不一致但功能正确 | 风格偏好 |
| 前端 | 数据丢失 / 不可恢复的误操作 | 用户无法完成任务或被误导 | 体验受损 | 观感不一致 |

**分类的 impact 与单条规则的 impact 是两个维度**：分类的决定阅读顺序，单条的决定冲突时服从哪个。CRITICAL 分类里出现 HIGH 规则是正常的。

## 原子化

一条规则一个约定。判据是**触发条件是否相同**——同一时刻会同时想起来的才放一起。

```
❌ naming-conventions.md（包结构 + 类名 + 方法名 + URL + 表名，7.7 KB）
✅ naming-package-layout / naming-class-suffix / naming-controller-methods / naming-url / db-table-naming
```

拆分后每条有稳定 slug，可在代码审查里直接点名引用。

## 索引条目

索引里的一行摘要要写**触发条件**，不是复述标题：

```
❌ - `entity-tableid-assign-id` — 主键 ID 类型约定
✅ - `entity-tableid-assign-id` — 主键用 `IdType.ASSIGN_ID`，`AUTO` 在非 MySQL 下 INSERT 直接失败
```

agent 是靠这一行决定要不要读全文的。写成前者，它无从判断当前任务是否相关。

## 示例代码

- 用项目真实会出现的场景，不要 `foo` / `bar`
- 错误示例要标注**错在哪**，不能只贴代码
- 正确示例要能直接抄用
- 语言标注要准确（`java` / `tsx` / `sql` / `bash`），影响高亮

## 组织专属内容

通用 skill 里**不得**出现具体的组织名、平台名、邮箱域名、logo 规格、内部代号、具体类名表名。这些迁到项目的 CLAUDE.md。

判定：这行字换个公司还成立吗？
