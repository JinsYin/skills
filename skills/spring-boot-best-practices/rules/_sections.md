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
**Description:** Strict `Controller → Service → Mapper` one-way flow. Cross-layer calls break transaction boundaries, testability, and reuse together — costliest debt to unwind.

## 2. Cryptography (crypto)

**Impact:** CRITICAL
**Description:** Algorithm choice, key management, and logging discipline for ShangMi SM2/SM3/SM4. Violations create exploitable vulnerabilities often caught only in production.

## 3. Entities & Persistence (entity)

**Impact:** CRITICAL
**Description:** MyBatis-Plus primary-key strategy and audit field fill. Wrong ID strategy fails `INSERT` at runtime with errors far from root cause.

## 4. Database & Migrations (db)

**Impact:** HIGH
**Description:** Table/column/index naming, Gauss driver and Flyway dependency selection, plus multi-dialect, multi-topology Flyway layering and parity. Missing dialect files or shard-local unique indexes fail only in target environments — usually production.

## 5. Response Envelopes & Error Codes (envelope)

**Impact:** HIGH
**Description:** `R` / `RList` / `RPage` selection and 6-digit error codes. Contract drift spills out to every caller.

## 6. DTO Conventions (dto)

**Impact:** HIGH
**Description:** Boundaries, validation, and mapping across `Request` / `Response` / `Query` / `Dto`. Mixing roles leaks internal fields or drops validation.

## 7. Naming Conventions (naming)

**Impact:** MEDIUM
**Description:** Package, class, method, and URL naming. Inconsistency adds constant reading friction.

## 8. Stack Baseline (stack)

**Impact:** LOW
**Description:** Dependency baseline, auth framework selection, Lombok idioms, module READMEs, and Java readability rules.
