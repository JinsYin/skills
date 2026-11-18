---
title: Keep Dto internal; split dual-purpose objects
impact: HIGH
tags: dto, response, boundary
---

## Keep Dto internal; split dual-purpose objects

`{Name}Dto` crosses Services and queue payloads. Controllers do not accept or return it. A class that is both the Service result and the HTTP body grows an internal field (cost price, hash, soft-delete) and the HTTP contract grows with it, with no error at the Controller.

```text
Service ↔ Service     Dto
Queue payload         Dto
Controller ↔ client   Request / Response / Query
```

Split a dual-purpose type into `Dto` plus `Response`. Map between them in the Converter.
