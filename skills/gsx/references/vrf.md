# `--vrf-review` / `--vrf-approved` — audit the round / release the gate

Both modes sit around a `checkpoint:human-verify` gate, pointing opposite ways: `--vrf-review` audits what the round actually changed *before* release (diagnose, don't act); `--vrf-approved` validates and replies the `<resume-signal>` so GSD can continue (reply, don't act). Gate location is the same for both — §0 below plus `common.md` §A.

**Shared boundary**: read + interview, or read + reply. No Edit/Write, no file writes, no gsd-executor, no commits, no branch switches. One checkpoint per run. Reply in Chinese.

## §0 — Locate the target gate (shared)

Numbering (`X.Y` = Phase X / Plan Y; `X.Y.Z` = the Zth `<task>`) and blank-arg inference per `common.md` §A. When the arg is blank there's one stronger signal beyond the general rules: if the executor just returned a `checkpoint:human-verify` gate message, that's the Plan. Otherwise read `.planning/STATE.md`'s `executing` active phase, glob its `*-PLAN.md`, and **keep only those with a `checkpoint:human-verify` task and no `*-SUMMARY.md` in the same dir**. Exactly 1 → use it; 0 or several → "无法唯一定位一个待放行的 checkpoint:human-verify 门禁，请给我 Plan / Task 编号" and stop. **Don't guess.**

---

# `--vrf-review` — layered change summary + overreach audit

At the end of a `checkpoint:human-verify` round, audit what changed across **frontend / backend / database**, and surface one hidden risk: **problems that should have been fixed in the backend or database but were patched in the frontend.** These look fine in a browser but fail the moment someone calls the API directly — validation absent, translations and defaults missing, sensitive fields still returned.

Flow: summarize by layer → flag risks → interview the user → record decisions. **No code edits, no gsd-executor, no commits, no file writes** — conversation only. Acting on flagged items is the user's call (follow up with `gsx --quick`).

## 0 — Locate the scope (read-only)

Use the arg if given; otherwise locate the active phase's checkpoint task per §0 and read its `<what-built>` + `<how-to-verify>` — the "should-be" baseline. Not found (no `.planning/`, or no checkpoint task) → "无法定位 checkpoint:human-verify task —— 请指定 phase / checkpoint" and stop. Don't guess.

**The acceptance period is everything done in this conversation since the user began running `<how-to-verify>` and reporting issues, plus every fix you made.** Conversation context is the primary source; git is the cross-check. **Don't fabricate.**

## 1 — Reconstruct and classify by layer

List every change in that period, cross-checking with git:

```bash
git status --short      # uncommitted
git diff --stat         # uncommitted file list
git log --oneline -20   # commits this period
```

| Layer | Criteria | Typical paths |
|-------|----------|---------------|
| Frontend | React pages / components / API clients / utils / styles | `dap-frontend/src/...` |
| Backend | Controller / Service / Mapper / DTO·Request·Response / enums / config | `dap-server/dap-*/src/main/java/...` |
| Database | table create/alter/index/migration/seed SQL | `*.sql`, migration dirs, docker init |

One small table per layer: `file:line · what changed · which feedback it addressed`. No changes in a layer → "（本轮无改动）".

## 2 — Risk audit: frontend patches that should go deeper

The core step. For **every frontend change**, ask: is this covering a backend or database deficiency?

**Before flagging, actually read the backend code** (Grep/Read the Request DTO / Controller / Service / enum / entity) to confirm the guard is genuinely missing. A backend that already guards it is compliant, not a risk. **Only flag when the backend truly lacks it.**

| Frontend changed | Risk | Should land at |
|-----------------|------|----------------|
| **Field validation** (required/format/length/range) | a direct API call bypasses the browser → no validation | DTO `@NotBlank/@Pattern/@Size/@Min/@Max`; hard constraints also DB `NOT NULL/UNIQUE/CHECK` |
| **Enum/code → label** (zh↔en) | a hardcoded `code→中文` map; every consumer rewrites it; new values drift | backend enum (`@Getter` label) → `xxxLabel` at VO/Response assembly, or a dict table |
| **Default values** | a direct API call returns null | DTO default / Service fallback / DB column `DEFAULT` |
| **Uniqueness/dedup** (frontend scans the loaded list) | races; only the current page; not a real constraint | DB `UNIQUE uk_xxx` + backend catches the conflict → `BizException` |
| **List filter/sort/paginate** (in frontend memory) | only the current page; breaks at scale; unfiltered data was still sent | backend query params + SQL `WHERE/ORDER BY/LIMIT` |
| **Masking / hiding sensitive data** (frontend redacts) | the full plaintext is still in the response, visible in DevTools | backend strips or masks before returning, or the Response DTO omits the field |
| **Permission / button visibility** (frontend hides or disables) | the API is still directly callable | Spring Security `@PreAuthorize` / Sa-Token `@SaCheckPermission/@SaCheckRole` |
| **Error messages** (frontend invents copy for a status code) | copy drifts; other clients see only the raw code | backend `ErrorCode` with a Chinese `defaultMessage` |
| **Computed / derived fields** (frontend computes total/count/status) | every client computes independently and may disagree | backend computes at VO/Response assembly |

**Not a risk (don't false-flag)**: layout, spacing, colors, animations; pure display formatting (dates as `2026-04-23`); interaction details (drawer, focus, toast timing); routing; frontend-owned i18n copy — those are the frontend's job by design.

**Distinguish intentional design from oversight**: if `<how-to-verify>` or `threat_model` states a behavior is by design (e.g. the SK returned in plaintext once at creation), it isn't a risk.

## 3 — Interview per flagged risk

No risks → skip to step 4 and note "未发现风险".

For each risk, use `AskUserQuestion` **one at a time** (≤4 per call; chain calls). Explain what the frontend changed, why it's a risk, and where it should land (endpoint / Controller.method / VO field / table column).

Options:

1. `认可 —— 记为后端/数据库 TODO` (first; mark "(Recommended)" when the risk is genuine)
2. `前端这样就行 —— 后端已有保障 / 此处可接受`
3. `暂缓 —— 待讨论`

The user may use "Other". **Record only, do not act.**

## 4 — Output the summary (conversation only)

```
## 验收小结 —— <checkpoint / phase name>

### 一、本轮改动
**前端**（N 处）
| file:line | 改了什么 | 对应反馈 |
**后端**（N 处 / 本轮无改动）
**数据库**（N 处 / 本轮无改动）

### 二、风险审计（本该往下沉的前端补丁）
> 未发现风险 ——（or list each:）
**风险 1：<one-liner>**
- 现状：前端 <file:line> 做了 <…>
- 风险：<why>
- 应落在：<endpoint / Controller.method / VO field / table column>
- 你的决定：<the user's own words>

### 三、后续建议
> The items the user agreed to, as a checklist (**not dispatched** — follow up with gsx --quick).
```

## Guardrails (`--vrf-review`)

- Read and interview only. No Edit/Write, no file writes, no gsd-executor, no commits, no branch switches.
- **Read the backend code before flagging.** Under-report rather than over-report; uncertain → `暂缓 —— 待讨论`.

---

# `--vrf-approved` — release the gate

Locate → validate → reply the resume signal. Nothing else: no code edits, no file writes, no verification scripts, no SUMMARY, no commits, no branch switches — close-out after the signal belongs to GSD.

> **Prerequisite**: the user should have **actually run** `<how-to-verify>` and confirmed it passes. This mode does not test on their behalf. **If issues were found, don't use this mode** — describe the problem to GSD directly instead.

## 0 — Locate the target gate

See §0.

## 1 — Validate it's an unreleased `checkpoint:human-verify` gate

Read all the Plan's `<task>` elements in document order and check each `type`.

**Plan number (`X.Y`)**:

- At least one `type="checkpoint:human-verify"` → pass; record the index, `<name>`, `<what-built>`, `<resume-signal>`.
- No `checkpoint:*` task at all (pure `auto`) → refuse: "Plan 0X-0Y 没有 checkpoint:human-verify task，不需要人工放行 —— 这是全自动 Plan，executor 会自己收尾。"

**Task number (`X.Y.Z`)**:

- The Zth is `checkpoint:human-verify` → pass.
- The Zth is `auto` or other → refuse and **point to the real gate**: "Task X.Y.Z 是 auto 任务（『<name>』），不是人工验证门禁。门禁是 Task X.Y.N（『<gate name>』），要放行那一个。"
- The Zth doesn't exist (Z > task count) → refuse and tell the user the Plan's task count.

**Already released**: a `*-SUMMARY.md` in the same dir means it probably was. **Do not** re-signal. Ask first: "Plan 0X-0Y 已经有 SUMMARY.md，门禁看起来已放行/已关闭。要再放行一次吗？" and wait for explicit confirmation.

`gate="blocking-human"` gates (e.g. the npm legitimacy check) are releasable — the user invoking this mode *is* the "human-verified" act — but step 2 must display the `<how-to-verify>` items **in full** so they can confirm they checked them.

## 2 — Show the release scope, reply the resume signal

Give a concise auditable summary:

```
## 放行 checkpoint:human-verify —— Plan 0X-0Y / Task X.Y.Z
- 门禁 task：  Task N · <task name>
- 验收内容：  <1-2 sentence summary>
- Resume 信号：<resume-signal verbatim>
```

**Read the exact word in `<resume-signal>`** (usually quoted, e.g. `approved`; some use `verified`) and reply *that* word, not a default. Output it as the **last standalone line**:

```
✅ 已放行 Plan 0X-0Y（Task N）的 checkpoint:human-verify 门禁。GSD 可以继续收尾（验证 → SUMMARY.md → STATE.md → 提交文档）。

approved
```

> The last line is the signal. If `<resume-signal>` requires a different word, replace it.

If the session has **no** blocked GSD flow waiting (restarted, context lost), the signal won't auto-continue. Add: "未检测到被阻塞的 GSD 执行流 —— 要继续请重跑 `/gsd:execute-phase <phase>`，它会发现这个 checkpoint 已放行并继续收尾。"

## Refusal cases

Do **not** reply the signal — explain honestly and stop — when:

- There's no `.planning/` (not a GSD project).
- The Plan/Task number matches no file or task.
- The target Plan has no `checkpoint:human-verify` task (fully automatic).
- The given Task isn't `checkpoint:human-verify` (also point out the real gate index).
- The args are blank and no pending gate can be uniquely located.
- A `SUMMARY.md` already exists — confirm with the user first.

## Guardrails (`--vrf-approved`)

- Read and reply only. No Edit/Write, no build/test scripts, no SUMMARY, no commits, no branch switches — close-out is GSD's.
- **The prerequisite is that the user really completed `<how-to-verify>`.** Don't accept on their behalf; if issues were found, they should describe the problem instead of using this mode.
- Validation fails → refuse, **don't approximate** — a wrong signal continues the wrong Plan or task.
- Reply the exact word `<resume-signal>` requires; don't assume `approved`.
