---
title: Declare driver and Drizzle only in packages that use them
impact: HIGH
tags: db, dependency, pnpm, workspace, drizzle
---

## Declare driver and Drizzle only in packages that use them

Declare `pg` (the `gaussdb-nodejs` alias), `drizzle-orm`, and `drizzle-kit` only in the workspace package that opens a pool or runs migrations. Put versions in the pnpm catalog, not copied into every `package.json`. A root dependency is installed for every package and drags the native-less but still Gauss-specific driver into libraries that never talk to a database.

The `pg` override and `peerDependencyRules` stay at the workspace root so a transitive `pg` cannot resolve to upstream `node-postgres` beside the alias (see `db-gauss-driver-selection`).

**Wrong:**

```json
{ "name": "shared-dto", "dependencies": { "drizzle-orm": "0.45.4", "pg": "npm:gaussdb-nodejs@0.2.3" } }
```

**Right:** the API package and the migrator package depend on `drizzle-orm` and `pg`. A shared `libs/contracts` package depends on neither.
