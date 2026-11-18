---
title: Use base + overlay for multi-topology databases instead of duplicating full migration sets
impact: HIGH
impactDescription: Duplicated migration trees inevitably drift and fail only in the other topology
tags: db, migration, flyway, multi-dialect, overlay
---

## Use base + overlay for multi-topology databases instead of duplicating full migration sets

When one DB family spans multiple deployment topologies (distributed cluster / centralized primary-standby / standalone) and only a few DDL statements diverge, split migrations into `base + overlay` — **never duplicate full migration trees per topology**. N full copies require N synchronized edits per change; missing one passes locally and fails only when another topology boots.

Two tiers:

| Tier | Contents |
|---|---|
| `<db>-base` | **Shared baseline**: `CREATE TABLE`, seed data, `ALTER`, comments — all DDL valid across topologies |
| `<db>-<topology>` overlay | **Only divergent migrations**, one directory per topology with identical version numbers and names |

**Overlays are mutually exclusive**: active Flyway locations are always `base + one overlay`, never two overlays at build or runtime. Every version number **must appear in at most one active location** — duplicate versions across `base` and overlay abort Flyway startup.

Keep two questions separate:

**1. `base` or `overlay`?** Judge by whether portable syntax exists — not whether distributed concepts appear:

- Portable syntax exists → keep in `base`. Example: inline `CONSTRAINT uk_x UNIQUE(...)` on new table builds global index on distributed DBs and regular constraint on standalone DBs.
- No portable syntax → fork into `overlay`. Example: non-distribution-key unique index on **existing** table needs `CREATE GLOBAL UNIQUE INDEX ... DISTRIBUTE BY HASH(...)` on distributed clusters, rejected on standalone engines.

**2. How many overlays?** One **per deployment target**, even if two targets execute identical SQL today. Question 1 sets `base` vs `overlay` boundary; Question 2 sets overlay granularity.

1-to-1 profile ↔ location parity prevents unverified mental remapping: if `gauss-centralized` secretly serves both centralized GaussDB and standalone openGauss, operators editing `SPRING_FLYWAY_LOCATIONS` guess a mapping nothing checks. One extra overlay file checked via `diff` costs far less than misrouting prod migrations.

> Equivalent overlays may differ in target-product SQL comments, but editing comments on applied migrations alters Flyway checksums — see `db-migration-immutable-after-apply`.

**Wrong (duplicating new table across two overlays):**

```
gauss-distributed/V25__add_authcode_agreement.sql   -- 60-line CREATE TABLE + 3-line GSI
gauss-centralized/V25__add_authcode_agreement.sql   -- 60-line CREATE TABLE + 2-line index
```

60 duplicated DDL lines drift next time a column is added.

**Right (push portable DDL into `base`):**

```
gauss-base/V25__add_authcode_agreement.sql          -- CREATE TABLE with inline CONSTRAINT UNIQUE
```

Keep files in overlays only when syntax diverges, and keep sibling overlays **byte-identical outside divergent DDL and header comments**. Run pairwise `diff` after every overlay edit.

See also `db-migration-parity`, `db-migration-locations-injection`, `db-distributed-unique-index`, `db-migration-immutable-after-apply`.
