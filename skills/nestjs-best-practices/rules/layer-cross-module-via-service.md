---
title: Cross-module calls go through the exported Service
impact: CRITICAL
tags: layer, module, service, repository, exports
---

## Cross-module calls go through the exported Service

A feature module exports its Service only. Callers import that module and inject the Service. Exporting a Repository, a Drizzle table, or the database handle lets another module skip validation, cache eviction, and `@Transactional()` rules.

**Wrong:**

```ts
@Module({
  providers: [OrderService, OrderRepository],
  exports: [OrderRepository], // ❌ callers bypass OrderService
})
export class OrderModule {}
```

**Right:**

```ts
@Module({
  providers: [OrderService, OrderRepository],
  exports: [OrderService],
})
export class OrderModule {}
```

```ts
constructor(
  private readonly orderRepository: OrderRepository, // own module
  private readonly userService: UserService,         // other module
) {}
```

Drizzle table objects stay module-private. A join that needs another module's table is a sign the other module should expose a Service method that returns a `Dto`.
