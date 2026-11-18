---
title: Controller method names and declaration order
impact: MEDIUM
tags: naming, controller, crud
---

## Controller method names and declaration order

Use fixed **resource-free** CRUD verbs (`create`, never `createUser` — Controller class already names resource):

`page` (paginated) / `list` (full list) / `select` (dropdown options) / `get` / `create` / `update` / `delete` (hard delete) / `remove` (soft delete)

Use `{verb}{Resource}` for non-CRUD domain actions: `cancelProcess`, `resetPassword`.

**Fix declaration order**: all CRUD methods before non-CRUD actions, ordered `page → list → select → get → create → update → delete/remove` so every Controller reads in identical order.

```java
@GetMapping                    public RPage<UserListItemResponse> page(...)
@GetMapping("/all")            public RList<UserListItemResponse> list(...)  // cap max rows to prevent OOM
@GetMapping("/options")        public RList<UserOptionResponse> select()
@GetMapping("/{id}")           public R<UserDetailResponse> get(...)
@PostMapping                   public R<UserCreateResponse> create(...)
@PutMapping("/{id}")           public R<Boolean> update(...)
@DeleteMapping("/{id}")        public R<Boolean> remove(...)
```

Never declare both `delete` and `remove` on one Controller — mixing hard-delete and soft-delete verbs invites wrong deletion calls.
