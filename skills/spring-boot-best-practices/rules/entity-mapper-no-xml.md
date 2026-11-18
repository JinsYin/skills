---
title: No Mapper XML or raw full-statement SQL
impact: HIGH
tags: entity, mapper, mybatis-plus, mpj, sql
---

## No Mapper XML or raw full-statement SQL

Extend `MPJBaseMapper<Entity>` on Mappers and build queries with MyBatis-Plus wrappers and MPJ APIs (`selectJoinPage`, `leftJoin`, `selectAs`) — no Mapper XML or raw full-statement SQL. Handwritten full SQL binds to one dialect and forks across multi-DB targets.

**Wrong:**

```java
@Mapper
public interface UserMapper extends MPJBaseMapper<UserEntity> {
    @Select("SELECT * FROM t_user WHERE status = #{status} LIMIT 10") // ❌ dialect-specific SQL
    List<UserEntity> listByStatus(String status);
}
```

**Right:**

```java
@Mapper
public interface UserMapper extends MPJBaseMapper<UserEntity> {
}

// Build queries with wrappers inside the Service
LambdaQueryWrapper<UserEntity> w = Wrappers.lambdaQuery(UserEntity.class)
        .eq(UserEntity::getStatus, status)
        .last("LIMIT 10");
```

When complex projections or aggregations cannot use wrappers alone, small bound SQL fragments inside wrappers are allowed — keep parameters bound (never concatenated) and comment equivalent SQL shape next to it.
