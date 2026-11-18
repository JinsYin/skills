---
title: Applied migrations are immutable — Drizzle will not tell you
impact: HIGH
impactDescription: Edited migrations silently diverge schema between existing and fresh environments
tags: db, migration, drizzle, hash, drift
---

## Applied migrations are immutable — Drizzle will not tell you

Drizzle records `hash` and `created_at` in `drizzle.__drizzle_migrations`, then decides what to run by comparing timestamps only:

```text
if (lastCreatedAt < migration.folderMillis) { execute(sql); insert hash }
```

An edited file whose `when` is already applied is **not** executed again, and the stored hash is **not** checked. Fresh databases run the new text; existing databases keep the old schema. There is no `repair` command. A comment-only edit is already drift.

Applied SQL is read-only. Ship a new generated migration. Do not disable this by deleting rows from `__drizzle_migrations`.

`folderMillis` is the `when` field in `meta/_journal.json`, not the numeric prefix in the filename.
