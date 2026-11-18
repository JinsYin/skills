---
title: Use ASSIGN_ID for primary keys, never AUTO
impact: CRITICAL
impactDescription: INSERT fails immediately on non-MySQL targets
tags: entity, mybatis-plus, primary-key, opengauss
---

## Use ASSIGN_ID for primary keys, never AUTO

Use `IdType.ASSIGN_ID` so app layer generates Snowflake IDs independent of DB engine — never `IdType.AUTO`. On non-MySQL DBs (e.g., openGauss `BIGSERIAL` differs from MySQL `AUTO_INCREMENT` under JDBC key generation), `AUTO` omits `id` and `INSERT` hits `NOT NULL`, throwing constraint errors far from root cause.

**Wrong:**

```java
@TableId(type = IdType.AUTO) // ❌ coupled to DB auto-increment
private Long id;
```

**Right:**

```java
@TableId(type = IdType.ASSIGN_ID)
private Long id;
```

**Exception** — use `IdType.INPUT` when primary key reuses external business ID:

```java
@TableId(value = "app_id", type = IdType.INPUT)
private Long appId;
```
