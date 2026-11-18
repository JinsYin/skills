---
title: Populate audit timestamps via @TableField(fill)
impact: CRITICAL
impactDescription: Audit timestamp columns become NULL or stale across dialects
tags: entity, mybatis-plus, audit, opengauss
---

## Populate audit timestamps via @TableField(fill)

Populate audit timestamps in app layer via MyBatis-Plus `MetaObjectHandler` + `@TableField(fill = ...)` — never rely on DB `ON UPDATE CURRENT_TIMESTAMP` (MySQL-only; stripped on Gauss-family DBs, leaving `updated_at` `NULL` or frozen).

**Wrong (relying on database DDL defaults/triggers):**

```java
private LocalDateTime createdAt; // ❌ no fill; relies on DB default
private LocalDateTime updatedAt;
```

**Right:**

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createdAt;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updatedAt;
```

Mark `createdAt` with `FieldFill.INSERT` and `updatedAt` with `FieldFill.INSERT_UPDATE`.
