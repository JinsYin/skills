---
title: One-way layered dependencies
impact: CRITICAL
tags: layer, architecture, controller, service, mapper
---

## One-way layered dependencies

`Controller → Service → Mapper`: each layer depends only on adjacent lower layer. Reverse or skip-layer calls break transaction boundaries, unit testability, and reuse at once.

| Layer | Responsibility | Forbidden |
|---|---|---|
| Controller | HTTP contract: routing, binding, validation, auth | Calling Mappers; calling other Controllers |
| Service | Business logic, transactions, orchestration, external calls, caching | HTTP/view concerns; injecting another domain's Mapper |
| Mapper | Database access and ORM mapping | Business rules, validation, transaction control |

**Wrong (Controller injects Mapper directly, bypassing transactions and domain checks):**

```java
@RestController
@RequiredArgsConstructor
public class UserController {
    private final UserMapper userMapper; // ❌ skips Service layer
    @GetMapping("/users/{id}")
    public R<UserEntity> get(@PathVariable Long id) {
        return R.ok(userMapper.selectById(id));
    }
}
```

**Right:**

```java
@RestController
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;
    @GetMapping("/users/{id}")
    public R<UserDetailResponse> get(@PathVariable Long id) {
        return R.ok(userService.getById(id));
    }
}
```
