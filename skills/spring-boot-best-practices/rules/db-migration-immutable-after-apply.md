---
title: Applied migrations are immutable — even comment edits change checksums
impact: HIGH
impactDescription: Checksum mismatch aborts startup in every environment that already ran the migration
tags: db, migration, flyway, checksum, repair
---

## Applied migrations are immutable — even comment edits change checksums

Flyway hashes **entire file contents** (comments, blank lines, indentation). Editing an applied migration fails `validate` on next boot — **only in environments that already ran it**: fresh environments migrate clean while existing environments (usually prod) fail to start.

Default rule: **applied migrations are read-only; ship changes as `V<n+1>__fix_xxx.sql`**.

Sole exception: non-functional edits that **do not change executed SQL** (comments, formatting, target-product labels). Do not ship an empty `V<n+1>`; accept checksum change and run `repair` before `migrate` on every environment that already applied that version:

```bash
flyway repair   # rewrites checksums in flyway_schema_history from current file contents
flyway migrate
```

In Spring Boot, use `spring.flyway.repair-on-migrate` or a pre-deploy repair job, and **record the repair step in release notes** — skipping it crashes next rolling deploy long after the edit.

**Never disable validation to bypass checksum errors:**

```yaml
# ❌ Silences real schema drift alongside your comment edit
spring.flyway.validate-on-migrate: false
```

`validate-on-migrate: false` hides manual prod DDL drift and deleted migration files — the exact bugs validation catches. If a legacy project already disabled it, still document `repair` in release notes since no automatic check will warn operators.
