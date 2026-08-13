---
title: 同库多形态用 base + overlay，不复制整套迁移
impact: HIGH
impactDescription: 整套复制必然漂移，漂移只在另一形态的环境暴露
tags: db, migration, flyway, multi-dialect, overlay
---

## 同库多形态用 base + overlay，不复制整套迁移

同一个数据库产品有多种部署形态（分布式集群 / 集中式主备 / 单机），而某些 DDL 只在其中一种形态下合法时，**不要为每种形态各维护一份完整迁移集**。N 份完整副本里绝大多数文件逐字相同，改一条要同步改 N 处——漏改不会在本地报错，只在另一形态的环境启动时炸。

拆成两层：

| 层 | 放什么 |
|---|---|
| `<db>-base` | **共通基线**：建表、种子、ALTER、注释——凡两种形态语法一致的，全部放这里 |
| `<db>-<形态>` overlay | **只放确实分叉的那几条**，每种形态一份，版本号与名称严格一致 |

激活的 location 是 `base + 某一个 overlay`。因此同一版本号**只能出现在一个激活 location**——base 与 overlay 之间绝不能重复版本号，否则 Flyway 报重复版本直接启动失败。

**何时才分叉**——判据是「有没有两端共通的写法」，不是「这条迁移涉不涉及分布式概念」：

- 有共通写法 → 留在 base。例：新建表的唯一约束写成表内联 `CONSTRAINT uk_x UNIQUE(...)`，分布式下自动建全局索引、单机下是普通约束，一份通吃。
- 确无共通写法 → 才分叉。例：对**既有**表追加非分布键唯一索引，分布式必须用 `CREATE GLOBAL UNIQUE INDEX ... DISTRIBUTE BY HASH(...)`，而单机不认这个语法。

**错误（同一张新表在两个 overlay 里各写一遍）：**

```
gauss-distributed/V25__add_authcode_agreement.sql   -- 建表 60 行 + 唯一索引 3 行
gauss-centralized/V25__add_authcode_agreement.sql   -- 建表 60 行 + 唯一索引 2 行
```

60 行建表体重复两份。下次给这张表加字段，改一处漏一处。

**正确（能共通的下沉到 base）：**

```
gauss-base/V25__add_authcode_agreement.sql          -- 建表，唯一约束写表内联 CONSTRAINT
```

只有真的无法共通时才留在 overlay，且**两份 overlay 除分叉语句外必须逐字一致**（建表体、ALTER、DROP、注释同步维护）。新增 overlay 后用 `diff` 核一遍是最省事的校验方式。

配套见 `db-migration-parity`（多方言同版本同步）、`db-migration-locations-injection`（location 怎么注入）、`db-distributed-unique-index`（分叉的根因）。
