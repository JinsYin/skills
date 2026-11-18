---
title: Cross-domain calls go through Service, never another domain's Mapper
impact: HIGH
tags: layer, service, mapper, coupling
---

## Cross-domain calls go through Service, never another domain's Mapper

Service may inject another Service, **never** another domain's Mapper. Bypassing owning Service skips its validation, cache eviction, and transaction invariants — bugs hidden until other domain changes.

**Wrong:**

```java
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;
    private final RoleMapper roleMapper; // ❌ bypasses RoleService
}
```

**Right:**

```java
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;   // own domain's Mapper
    private final RoleService roleService; // cross-domain via Service
}
```
