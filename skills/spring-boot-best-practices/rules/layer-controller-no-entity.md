---
title: Controllers must never return Entities
impact: CRITICAL
impactDescription: Leaks sensitive columns
tags: layer, controller, entity, response, security
---

## Controllers must never return Entities

Return view-specific `Response` types from Controllers, never `Entity`. Entity maps every table column (password hashes, soft-delete flags, internal audit fields); returning it exposes sensitive data, and adding table columns later silently widens public API output.

**Wrong (exposing raw table row):**

```java
@GetMapping("/users/{id}")
public R<UserEntity> get(@PathVariable Long id) {
    return R.ok(userService.getEntityById(id)); // ❌ includes password / deleted
}
```

**Right (view-specific Response with explicit fields):**

```java
@GetMapping("/users/{id}")
public R<UserDetailResponse> get(@PathVariable Long id) {
    return R.ok(userService.getById(id));
}
```

Service methods must also return `Response`, `Dto`, or primitives — **never** `Entity`, or leak risk shifts up into Controller.
