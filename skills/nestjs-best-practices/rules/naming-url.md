---
title: Lowercase kebab-case plural URLs
impact: MEDIUM
tags: naming, url, http
---

## Lowercase kebab-case plural URLs

- Segments are lowercase kebab-case: `/order-items`.
- Resource nouns are plural: `/users`, `/orders`.
- One resource: `GET /users/:id`. Collection: `GET /users`.
- Non-CRUD action: `POST /orders/:id/cancel`. Not `/cancelOrder`.

| Query | Path |
|---|---|
| Paginated | `GET /users` |
| Full list | `GET /users/all` |
| Dropdown | `GET /users/options` |

The global prefix (`api`) is set once in bootstrap, not repeated on each `@Controller`. URLs are plural collections; classes and tables stay singular.
