---
title: One feature module per folder
impact: MEDIUM
tags: naming, module, layout
---

## One feature module per folder

Nest modules are feature folders, not a global `controllers/` + `services/` split. Each feature owns its Controller, Service, Repository, table, and converter. HTTP types sit in `dto/` inside that folder.

```text
src/order/
  order.module.ts
  order.controller.ts
  order.service.ts
  order.repository.ts
  order.table.ts
  order.converter.ts
  dto/
    order-create.request.ts
    order-detail.response.ts
    order-page.query.ts
```

Shared technical pieces (`R`, `BizException`, `DbModule`, guards, `PageQuery`) live under `src/shared/` or a workspace lib. They do not accumulate feature tables. Cross-feature calls follow `layer-cross-module-via-service`.
