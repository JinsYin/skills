---
name: gsx-vrf-review
description: "Summarize what a GSD checkpoint:human-verify round changed across frontend / backend / database, and surface frontend-only patches that should have landed in backend/DB (field validation, enum/code zh↔en mapping, defaults, uniqueness, masking, permission visibility), interviewing the user per risk. Diagnostic only — no edits, no executor, no commits, no file writes. Invoke explicitly at a round's end: 'summarize what this round changed', 'acceptance summary', 'did this round have anything that should have been a backend change', 'gsx-vrf-review'. Sibling: gsx-vrf-autorun runs the verify steps; gsx-vrf-approved releases the gate."
argument-hint: "[optional: checkpoint / phase to summarize; auto-locates the active phase if blank]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# gsx-vrf-review

## Codex Adapter

In Codex, translate this Claude wrapper instead of rewriting it:

- `$ARGUMENTS` = text after `$gsx-*`.
- `/gsd:<name> ...` or `Skill("gsd:<name>", args="...")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options/plans, first print each option's core content in your reply, then list the choices as a numbered Markdown list and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.
- Preserve wrapper boundaries; if GSD owns edits, do not edit source here.


At the end of a GSD `checkpoint:human-verify` round, audit what changed across **frontend / backend / database**, and surface a hidden risk: **problems that should have been fixed in backend/DB but were patched in the frontend.** These look fine in-browser but fail when the API is called directly — validation absent, translations/defaults missing, sensitive fields still exposed.

Flow: summarize by layer → flag risks → interview user → record decisions. **No code edits, no gsd-executor, no commits, no file writes** — conversation only. Acting on flagged items is the user's call (follow up with `/gsd:quick`).

## 0 — Locate scope (read-only)

`$ARGUMENTS` given → use it. Else auto-locate:
1. Read `.planning/STATE.md` for the `executing` active phase.
2. In `.planning/phases/<phase>/`, find `*-PLAN.md` with `<task type="checkpoint:human-verify">`; read its `<what-built>` + `<how-to-verify>` — the "should-be" baseline.
3. Not found (no `.planning/`, or no checkpoint task) → "Could not locate a checkpoint:human-verify task — please specify the phase / checkpoint." and stop. Do not guess.

**Acceptance period = everything done in this conversation since the user began running `<how-to-verify>` and reporting issues, plus all fixes you made.** Conversation context is the primary source; git is a cross-check. Don't fabricate.

## 1 — Reconstruct and layer-classify changes

List every change this period; cross-check git:
```bash
git status --short      # uncommitted
git diff --stat         # uncommitted file list
git log --oneline -20   # commits this period
```

| Layer | Criteria | Typical paths |
|-------|----------|---------------|
| Frontend | React pages/components/API clients/utils/styles | `dap-frontend/src/...` |
| Backend | Controller/Service/Mapper/DTO·Request·Response/enums/config | `dap-server/dap-*/src/main/java/...` |
| Database | table create/alter/index/migration/seed SQL | `*.sql`, migration dirs, docker init |

Per layer, a small table: `file:line · what changed · which feedback it addressed`. No changes → "(no changes this round)".

## 2 — Risk audit: frontend-only patches that should go deeper

Core step. For **every frontend change**, ask: is this covering a backend/DB deficiency?

**Before flagging, actually read the backend code** (Grep/Read the Request DTO / Controller / Service / enum / entity) to confirm the backend lacks the guard. Backend already guarded = compliant, not a risk. Only flag when the backend genuinely lacks it.

| Frontend changed | Risk | Should land |
|-----------------|------|-------------|
| **Field validation** (required/format/length/range) | direct API call bypasses browser → validation absent | DTO `@NotBlank/@Pattern/@Size/@Min/@Max`; hard constraints + DB `NOT NULL/UNIQUE/CHECK` |
| **Enum/code → label** (zh↔en) | hardcoded `code→中文` map; every consumer rewrites; new values drift | backend enum (`@Getter` label) → `xxxLabel` at VO/Response assembly; or dict table |
| **Default values** | direct API call → null | DTO default / Service fallback / DB column `DEFAULT` |
| **Uniqueness/dedup** (frontend scans loaded list) | races; only current page; not a real constraint | DB `UNIQUE uk_xxx` + backend catches conflict → `BizException` |
| **List filter/sort/paginate** (in-memory frontend) | only current page; breaks at scale; unfiltered data sent | backend query params + SQL `WHERE/ORDER BY/LIMIT` |
| **Masking/sensitive hide** (frontend redacts) | full plaintext still in response, visible in DevTools | backend strips/masks before return, or Response DTO omits field |
| **Permission/button visibility** (frontend hides/disables) | API still callable directly | Spring Security `@PreAuthorize` / Sa-Token `@SaCheckPermission/@SaCheckRole` |
| **Error messages** (frontend fabricates copy for status code) | copy drifts; other clients see raw code | backend `ErrorCode` Chinese `defaultMessage` |
| **Computed/derived fields** (frontend computes total/count/status) | each client computes independently, may disagree | backend computes at VO/Response assembly |

**NOT a risk (don't false-flag):** layout/spacing/colors/animations, pure display formatting (dates as `2026-04-23`), interaction details (drawer/focus/toast timing), routing, frontend-owned i18n text — frontend's job by design.

Distinguish **intentional design** from **oversight**: if `<how-to-verify>` or `threat_model` states a behavior is by design (e.g. SK plaintext returned once at creation), not a risk.

## 3 — Interview per flagged risk

No risks → skip to step 4, note "No risks found".

Per risk, `AskUserQuestion` **one at a time** (≤4/call; chain calls). Explain: what changed (frontend), why a risk, where it should land (endpoint / Controller.method / VO field / table column).

Options:
1. `Agree — mark as backend/database TODO` (first, "(Recommended)" when genuine)
2. `Frontend is fine — backend already safe / acceptable here`
3. `Defer — pending discussion`

User may use "Other". **Record only, do not act.**

## 4 — Output summary (conversation only, Chinese)

```
## Acceptance Summary — <checkpoint / phase name>

### I. Changes This Round
**Frontend** (N changes)
| file:line | what changed | feedback addressed |
**Backend** (N changes / no changes this round)
**Database** (N changes / no changes this round)

### II. Risk Audit (frontend-only patches that should go deeper)
> No risks found — (or list each:)
**Risk 1: <one-liner>**
- Current state: frontend <file:line> applied <…>
- Risk: <why>
- Should land at: <endpoint / Controller.method / VO field / table column>
- Your decision: <user's response verbatim>

### III. Follow-up Recommendations
> Items the user "agreed" to address, as a checklist (not dispatched — follow up via /gsd:quick).
```

## Guardrails

- Read and interview only. No Edit/Write, no file writes, no gsd-executor, no commit, no branch switch.
- Read backend code before flagging. Under-report over over-report; uncertain → "Defer — pending discussion".
- One checkpoint per run.
- Reply in Chinese.
