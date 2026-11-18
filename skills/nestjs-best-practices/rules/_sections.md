# Sections

Category order, impact levels, and scope. ID in parentheses = rule filename prefix.

Graded by **consequence of violation**, not frequency:

| Level | Meaning |
|---|---|
| CRITICAL | Immediate bug, security vulnerability, or startup/runtime failure |
| HIGH | Runs, but fails review and forces rework |
| MEDIUM | Inconsistent, though functionally valid |
| LOW | Style preference |

---

## 1. Layering Discipline (layer)

**Impact:** CRITICAL
**Description:** Strict `Controller → Service → Repository` one-way flow across feature modules. Cross-layer calls break transaction boundaries, testability, and reuse together — costliest debt to unwind.

## 2. Authentication & Authorization (auth)

**Impact:** CRITICAL
**Description:** Global default-deny guards, JWT verification, and password hashing. Opt-in guards fail open: one forgotten decorator ships a public endpoint.

## 3. Cryptography (crypto)

**Impact:** CRITICAL
**Description:** Algorithm choice, key management, and logging discipline for ShangMi SM2/SM3/SM4 via `sm-crypto-v2@2`. Violations create exploitable vulnerabilities often caught only in production.

## 4. ORM & Persistence (orm)

**Impact:** CRITICAL
**Description:** Drizzle primary keys, audit columns, transactions, and query building. Wrong ID mode corrupts IDs or crashes serialization; a missed transaction handle commits half a use case.

## 5. Database & Migrations (db)

**Impact:** HIGH
**Description:** `gaussdb-nodejs` driver and pool, Gauss-family dialect, drizzle-kit migration workflow with multi-topology base + overlay, plus table/column/index naming. Failures surface only in target environments — usually production.

## 6. Response Envelopes & Error Codes (envelope)

**Impact:** HIGH
**Description:** `R` / `RList` / `RPage` selection, global exception filter, and 6-digit error codes shared with Spring backends. Contract drift spills out to every caller.

## 7. DTO Conventions (dto)

**Impact:** HIGH
**Description:** Global validation, boundaries, and mapping across `Request` / `Response` / `Query` / `Dto`. Mixing roles leaks internal fields or drops validation.

## 8. Naming Conventions (naming)

**Impact:** MEDIUM
**Description:** File, class, method, URL, and feature-module layout naming. Inconsistency adds constant reading friction.

## 9. Stack Baseline (stack)

**Impact:** LOW
**Description:** Dependency baseline, config validation, bootstrap, logging, testing, pnpm workspace, and READMEs.
