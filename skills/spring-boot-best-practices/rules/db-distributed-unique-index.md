---
title: 分布式库的唯一约束必须含分布键，否则要全局索引
impact: HIGH
impactDescription: 普通唯一索引只在分片内唯一，跨分片重复数据能写进去
tags: db, migration, distributed, unique-index, gaussdb
---

## 分布式库的唯一约束必须含分布键，否则要全局索引

分布式数据库（GaussDB Distributed、TiDB、OceanBase 等）把数据按分布键散到各个分片。**普通唯一索引是分片本地的**——只保证同一分片内不重复。若唯一列不是分布键，两条同值记录落在不同分片时，本地索引各自看不到对方，重复数据照样写得进去。

这类故障最坏的形态是**静默**：不报错、不回滚，直到某天查出两条本该唯一的记录。

两种写法，按「表是不是本次新建」选：

**新建表——写成表内联约束，两种形态共通：**

```sql
CREATE TABLE t_authcode_agreement (
    auth_code   VARCHAR(64) NOT NULL,
    ...
    CONSTRAINT uk_authcode_agreement_auth_code UNIQUE (auth_code)
);
```

分布式下引擎自动建全局索引，单机下就是普通唯一约束——**一份 SQL 通吃**，无需在 overlay 里分叉（见 `db-migration-base-overlay`）。

**对既有表追加——必须显式全局唯一索引：**

```sql
-- ❌ 分布式下只在分片内唯一，跨分片可写入重复值
CREATE UNIQUE INDEX uk_org_name ON t_org(org_name);

-- ✅ 分布式：GSI，DISTRIBUTE BY 列与索引列一致
CREATE GLOBAL UNIQUE INDEX uk_org_name ON t_org(org_name) DISTRIBUTE BY HASH(org_name);
```

`CREATE GLOBAL UNIQUE INDEX` 语法在单机/集中式下不被认识，所以这一种情形——**且只有这一种**——需要分叉出集中式 overlay，改回普通 `CREATE UNIQUE INDEX`（无数据分布时它本身就是全表唯一）。

同理，`ALTER TABLE ... ADD UNIQUE` 在分布式下同样受「唯一键必须包含分布键」约束，不能当作绕过手段。
