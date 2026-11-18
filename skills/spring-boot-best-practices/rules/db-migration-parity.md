---
title: Keep multi-dialect migrations in lockstep at identical versions
impact: HIGH
impactDescription: Missing dialect files break only in the target environment
tags: db, migration, flyway, multi-dialect
---

## Keep multi-dialect migrations in lockstep at identical versions

In multi-DB projects, maintain every migration across **every active dialect location** with identical version numbers and names. Missing one dialect stays green locally while Flyway aborts startup or drifts schema in target environment — usually prod.

Invariants:

- Each version number **appears in at most one active location**, else Flyway aborts on duplicate version.
- Sibling dialect files match word-for-word outside SQL dialect differences (sync `CREATE TABLE`, `ALTER`, comments).
- Inject active locations via build profiles; never hardcode in Java/YAML.

**Checklist when adding migration** — confirm every dialect directory has matching file and no active location set collides on version numbers.

When one DB family spans multiple topologies (distributed / centralized / standalone), use `base + overlay` (`db-migration-base-overlay`). Follow project `CLAUDE.md` for exact location hierarchy.
