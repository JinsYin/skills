---
title: Lowercase kebab-case plural URLs
impact: MEDIUM
tags: naming, url, rest, api
---

## Lowercase kebab-case plural URLs

- Lowercase **kebab-case** segments: `/order-items`.
- **Plural** resource nouns: `/orders`, `/users`, `/roles`.
- Single resource: `GET /orders/{id}`; collection: `GET /orders`.
- Non-CRUD actions: `POST /orders/{id}/cancel` — **never** RPC-style verb paths like `/cancelOrder`.

Standard query paths:

| Query shape | Path | Notes |
|---|---|---|
| Paginated | `GET /roles` | Never `/roles/page` |
| Full list | `GET /roles/all` | Cap max rows to prevent OOM |
| Dropdown options | `GET /roles/options` | Return `{id, name}` pairs only |

URLs use plural nouns (resource collections) while Java classes/Entities use singular nouns (single instances).
