---
title: Package by technical role first, then by domain under dto
impact: MEDIUM
tags: naming, package, structure
---

## Package by technical role first, then by domain under dto

- First-level subpackages by **technical role**: `controller`, `service`, `mapper`, `entity`, `converter`, `config`, `constants`, `enums`, `exception`, `utils`.
- Second-level subpackages by **domain noun** under `dto` only (`dto/order/`, `dto/user/`).

Keep Controllers, Services, and Mappers directly under role root without domain subpackages — one class per domain needs no extra directory depth.

```
com.example.app
├── controller/OrderController.java
├── service/OrderService.java
├── service/impl/OrderServiceImpl.java
├── mapper/OrderMapper.java
├── entity/OrderEntity.java
└── dto/order/OrderCreateRequest.java
```
