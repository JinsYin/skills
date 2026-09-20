# `--uat-autorun` / `--vrf-autorun` — machine-run the verification

Both modes share one execution protocol (§E: cold start, Playwright, curl, judgment). They differ in what they run and where results go:

| | `--uat-autorun` | `--vrf-autorun` |
|---|---|---|
| Target | every case under the UAT file's `## Tests` | a `checkpoint:human-verify` task's `<how-to-verify>` steps |
| Output | **writes back live to that same UAT file** (`result`/`note`/Summary/Gaps) | **a conversation-only report**; writes no files |
| States | native four: `pass`/`issue`/`skipped`/`blocked` | `pass`/`fail`/`skip`/`blocked` |
| Close-out | turns each `issue` into a `## Gaps` entry | tells the user to run `--vrf-approved` |

**Shared boundary (hard rules)**:

- **Test only, never fix.** A bug goes into the Gap section or the report; **never change business code** (fixes go to `gsx --quick` / `gsx --debug`).
- **Never release.** Never reply the `<resume-signal>`; on all-pass, prompt the user to run `gsx --vrf-approved`.
- No commits, no branch switches, no checkpoints.
- Test data is self-managed and **not force-cleaned** (kept for re-verification); say what was created in the `note` or report.
- Reply in Chinese.

---

# `--uat-autorun`

Run every case in the UAT file and write results back to the **same file, same fields**, using verify-work's native status words so that verify-work's continuation and `/gsd:plan-phase --gaps` keep recognizing them.

**Write back, never create**: only update an existing UAT file; if absent, tell the user to run `/gsd:verify-work {NN}` first.

## Execution model — Opus orchestrates, Sonnet executes

To minimize main-thread (Opus) tokens, **light orchestration** is split from **heavy execution**:

- **Orchestration (main thread / Opus)**: §0–§2 parse the Phase, locate and parse the UAT, classify cases, show the plan table; §2.5 hands execution to **one** Sonnet subagent; §6 presents the subagent's compact summary.
- **Execution (subagent / Sonnet)**: §3–§5 cold start, per-case Playwright/curl runs, UAT write-back, close-out. All the verbose tool output (a11y snapshots, `browser_network_requests`, full curl responses, cold-start log tails) stays in the subagent's context; the main thread only ever sees the plan table and the final summary — cheaper in tokens and cheaper per token.

The subagent is `general-purpose` (it carries Bash background tasks, Playwright MCP, and full Read/Write/Edit) with `model: "sonnet"`. It writes back to the **real** UAT file on disk, so live progress and interrupt-and-resume still work.

## 0–1 — Parse the Phase number and locate the UAT

Phase number per `common.md` §A (use `Active phase` when the tone says "test the current phase"); UAT location and structure per §B1/§B2.

Extract each case's **N**, **title** and **expected**. Existing `result` values are reference only — **re-run every case independently** (including manually-marked ones; actual results win). Also read `{NN}-CONTEXT.md` / `{NN}-*-SUMMARY.md` / `{NN}-PLAN.md` for the APIs and pages under test, credentials and initial data, and env prerequisites. The root `CLAUDE.md` "Local Run" section is the authoritative cold-start guide.

## 2 — Classify the cases

Use §E1's table to route each case, and §E2's rules to pick out what can't be machine-judged. Show a brief plan table (number / title / category), then go to §2.5.

## 2.5 — Spawn the Sonnet subagent

**Handle anything needing user interaction in the main thread first** (a subagent can't prompt conveniently): if there's a cold-start case whose `expected` demands a destructive op like "重置 DB / 删除 `docker/mysql|redis/data`", **`AskUserQuestion` now**. If the user declines, pass that decision to the subagent so it marks those cases `skipped` with `note: "DB reset required — not authorized."`.

Then spawn **one** Sonnet subagent for §3–§5. Its prompt must contain at least:

- **The execution protocol (single source of truth — don't restate it in the prompt)**: `阅读 <absolute path of this file> 的「§3–§5」「§E」与「## Guardrails」，严格按其执行` (you know the path, having just read it).
- **The absolute path of the target UAT file** (the one chosen in §1), with "only write back to this one file".
- **The Phase number and phase directory**, plus the context files to read (`{NN}-CONTEXT.md` / `{NN}-*-SUMMARY.md` / `{NN}-PLAN.md`, and the root `CLAUDE.md` "Local Run").
- **The classification plan**: each case's N / title / category — the §2 table.
- **The destructive-op decision** from the `AskUserQuestion` above.
- **Return requirements (critical for token savings)**: return only a compact summary — final Summary counts, the skipped/blocked list (one reason each), the Gap list (the `issue` cases). **Never** paste Playwright snapshots, `browser_network_requests`, full curl output, or logs back to the main thread.

Call it roughly as `Agent(subagent_type="general-purpose", model="sonnet", description="autorun Phase NN", prompt=<the above>)`. Its boundaries (test only / write back only the target UAT / four states only) load when it reads §3–§5 and the Guardrails, so don't restate them.

> Playwright MCP is a single browser instance: run **one** web-case subagent at a time; don't spawn several to fight over the browser.
> When the subagent finishes → §6.

> **§3–§5 below are the execution protocol, running in the Sonnet subagent's context** (or inline in a Codex setup with no subagents).

## 3 — Prepare the environment

Per §E3. Services failing or migration errors → cold-start cases get `result: issue` with a log excerpt in `note`; dependent cases get `result: blocked`, `note: "environment unavailable"`; stop trying.

## 4 — Run each case and write back

Run in `## Tests` order. **Per case: update Current Test → execute → write back result + note → update Summary**, then move on. Per-case writes give real-time progress and interruptible-resumable state.

**4.0 — Update Current Test**: `Edit` `## Current Test` to `number: N` / `name: <case title>` / `expected: |` (verbatim) / `awaiting: autotest running`.

**4.1 — Seed and execute**: seed per §E3, then run per §E4 (Web) / §E5 (API).

**4.2 — Judge**: per §E6, mapped onto the four states `pass` / `issue` / `skipped` / `blocked`.

**4.3 — Write this case back**: `Edit` the case block under `## Tests` (anchored on `### N. <title>`). **Every case writes both `result` and `note`** (one line of evidence): `pass` → "what was tested, what was observed"; `issue` → add a `severity` line plus "expected X, actual Y"; `skipped` → the skip reason; `blocked` → the blocking point and env reason. Example:

```
### 10. 全链路审计落库
expected: 请求后 t_audit_log 落 1 条含 log_type/latency_ms/...
result: issue
severity: major
note: 1 个请求落 2 条审计记录（id 28/29 内容相同），审计重复写入
```

`severity` (only for `issue`, judged from the actual consequence — don't ask) per `common.md` §C2.

**4.4 — Update Summary**: after each case, `Edit` `## Summary` (`total` unchanged; `passed`/`issues`/`skipped`/`blocked` accumulate; `pending` = cases not yet run) and bump frontmatter `updated`. Return to 4.0 for the next case.

## 5 — Close-out

1. **`## Current Test`** → `[autotest complete]`.
2. **`## Summary`** → confirm the counts match (`pending` = 0).
3. **frontmatter `status`** → no `pending`/`blocked` → `complete`; some `blocked` → `partial`. Bump `updated`.
4. **`## Gaps`** → append each `result: issue` case as verify-work YAML. `blocked`/`skipped` do **not** become Gaps — those are environment or judgment problems, not code defects. Fields: `truth` (the assertion distilled from expected), `status: failed`, `reason: "Autotest: <expected X, actual Y>"`, `severity`, `test` (case number), `artifacts: []`, `missing: []`. If the section was `[none yet]` or a placeholder → replace; otherwise append.
5. **Return to the orchestrator (compact)**: as the final message, return only the final Summary counts (total/passed/issues/skipped/blocked); the **skipped/blocked list** (one reason each, needing manual `/gsd:verify-work {NN}`); and the **Gap list** (the `issue` cases, fixed via `gsx --uat-quickfix` or `gsx --uat-planfix`). **Do not** paste raw tool output.

## 6 — Present the results (main thread / Opus)

When the subagent returns, the orchestrator **re-runs nothing** — relay its compact summary in Chinese: Summary counts, the skipped/blocked list (why each needs a human), the Gap list (how to fix). Remind the user that results were written back live to `{NN}-*UAT.md`, and that skipped items still need a manual `gsx --uat-phase {NN}` pass.

---

# `--vrf-autorun`

Machine-pre-run the `<how-to-verify>` checklist of a GSD `checkpoint:human-verify` gate (`gate="blocking"`). This is the step before `--vrf-approved`, which actually releases the gate.

**Extra boundary**: no writes or edits to `PLAN.md` / `STATE.md` / `SUMMARY.md`; the report is conversation-only.

## 0 — Parse args, locate the target gate

Numbering and blank-arg inference per `common.md` §A. Scope:

| User writes | Parsed as | Scope |
|-------------|-----------|-------|
| `4.4`, `Phase 4.4`, `Plan 4.4`, `04-04` | Phase 04 / Plan 04 | **all** human-verify tasks in that Plan |
| `Plan 4`, `Plan 04` | Plan 04 in the current Phase (conversation / STATE.md) | same |
| `4.4.1`, `Task 4.4.1` | Phase 04 / Plan 04 / 1st task | that task only (confirm it's human-verify) |
| `Task 3` | the 3rd task in the active Plan | that task only |

When the arg is blank, beyond §A's general inference there's a stronger signal: if the executor just returned a `checkpoint:human-verify` gate message, that's the Plan. Otherwise read STATE.md's `executing` active phase, glob its `*-PLAN.md`, and **keep only those with a `checkpoint:human-verify` task and no `*-SUMMARY.md` in the same dir**. Exactly 1 → use it; 0 or several → "无法唯一定位一个待放行的 checkpoint:human-verify 门禁，请给我 task / Plan 编号" and stop.

## 1 — Parse the `<how-to-verify>` steps

Read all the Plan's `<task>` elements in document order and check each `type`.

- **Plan number given** → filter every `type="checkpoint:human-verify"` task and verify each. None → "Plan 0X-0Y 没有 human-verify task" and stop.
- **Task number given** → take the Zth task. human-verify → verify it. `auto` or other → "Task X.Y.Z 不是 human-verify 门禁", **point out the real human-verify task index**, and stop (**don't silently switch**).

For each gate task extract: `<what-built>` (the feature scope being accepted); `<how-to-verify>` (**the core**: break into atomic steps, recording each expected observable result); `<resume-signal>` (for the report footer only — **never sent**).

Also read the same-dir `{NN}-CONTEXT.md` / `{NN}-*-SUMMARY.md` / `*-UI-SPEC.md` for APIs and pages under test, credentials, initial data, env prerequisites. The root `CLAUDE.md` "Local Run" is the authoritative cold-start guide.

## 2 — Classify the steps

Per §E1's table and §E2's skip rules. Then show a brief table (gate task / step # / summary / category) and continue.

## 3–4 — Prepare and execute

Per §E3 and §E4–§E5. Run in `<how-to-verify>` order — **data chains across steps, so respect it**. Judge per §E6, mapped onto `pass` / `fail` / `skip` / `blocked`.

Services failing or migration errors → mark the prep step `fail` with a log excerpt, mark dependent steps `blocked`, and stop trying.

## 5 — Output the report (conversation only)

Multiple gate tasks → one block each.

```markdown
## 自动验证报告 —— Plan 0X-0Y

### 门禁 Task N · <task name>
小结：共 M 步 · pass a · fail b · skip c · blocked d

| # | 步骤 | 类型 | 结果 | 说明 |
|---|------|------|------|------|
| 1 | ... | 准备/Web/API | pass/fail/skip/blocked | 实际结果 |

（repeat per human-verify task）

## 跳过的步骤（需人工跟进）
- Task N 步骤 K「<摘要>」—— 原因

## Gaps（发现的问题）
- Task N 步骤 M「<摘要>」—— fail：期望 X，实际 Y。修复走 gsx --quick 或 gsx --debug。
-（blocked 的环境问题与自动化盲区也列在这里）

## 本轮创建的测试数据
- 本轮创建的机构 / 应用 / 场景 / 凭据 / token。
```

The report **must** call out two things: (1) which steps were skipped and why; (2) the Gaps (fail/blocked plus automation blind spots).

**Closing prompt**:

- All pass, no skips or Gaps → "全部步骤通过 —— 你确认后跑 `gsx --vrf-approved` 放行。"
- Skips but no fail/blocked → "没发现问题，但有 N 步需人工跟进 —— 核实那几步后再放行。"
- Any fail/blocked → "发现 Gap —— 先修（`gsx --quick` 或 `gsx --debug`）并复验，再放行。"

**Always remind**: automated verification is not human judgment — review the skips first.

---

# §E Execution protocol (shared)

## E1 — Classify a step or case

| Category | Signals (expected / title / step text) | How to execute |
|----------|----------------------------------------|----------------|
| **Prep / cold start** | cold start / docker-compose / service up / Flyway migration / startup logs | **background tasks** (§E3), confirm readiness |
| **Web E2E** | UI behavior: page/console/list/drawer/button/click/toast/form validation/badge | **Playwright MCP** (§E4) |
| **Pure API** | HTTP contract: error codes, response fields, headers, `/openapi/*`, `/admin/*`, DB persistence | **curl** (+ `mysql`/`redis-cli`) (§E5) |
| **Skip** | see §E2 | `skipped` / `skip` |

## E2 — When to skip (can't be machine-determined)

- **Subjective with no objective anchor** — color or badge tint, "matches the prototype", polish, layout feel, animation.
- **Prerequisite not self-buildable** — real DID SDK, real upstream API, prod deploy/monitoring/backup, external third-party systems.
- **`expected` too vague** — no observable success criterion.
- **Mixed sub-items** — run the coverable part and mark the rest "partially skipped" in the `note`.

**When in doubt, prefer skip**, with the reason in the `note` or report.

## E3 — Prepare the environment (cold start)

**Probe first** (every case needs services online): `curl -s -o /dev/null -w "%{http_code}"` against :8080 and :3000.

**If there are cold-start cases**, the stack must start from stopped. **Stop first**: `docker-compose down` (**no `-v`** — keep the volumes), and kill running backend/frontend background processes. **Otherwise**: reuse what's online, start only what's down.

Follow `CLAUDE.md` "Local Run" via background tasks (`run_in_background`):

1. `docker-compose up -d` (MySQL 5.7 + Redis 7).
2. `cd dap-server && mvn -pl dap-common install -DskipTests` — installs the latest dap-common into `~/.m2` (foreground, wait).
3. `mvn -pl dap-admin spring-boot:run` — background (:8080); also `dap-gateway` (:8090) / `dap-transform` (:8091) if under test. **`spring-boot:run` cannot use `-am`; run it under `dap-server/`.**
4. `cd dap-frontend && pnpm install && pnpm dev` — background (:3000).
5. Poll: `curl` each port until it responds; check the logs for Flyway completion and no real `ERROR` (the benign macOS netty DNS warnings don't count).

> ⚠️ **Destructive ops need consent.** For an `expected` demanding "reset DB / delete `docker/mysql/data` or `docker/redis/data`": `--vrf-autorun` asks via `AskUserQuestion` on the spot; for `--uat-autorun` the authorization **was already confirmed by the orchestrator in §2.5 and passed in the prompt** (the subagent must **not** prompt again). Authorized → do it; not authorized → mark `skipped`/`skip` with `note: "DB reset required — not authorized."`. The local JDK must be 21; on a Java version error, switch `JAVA_HOME` per `CLAUDE.md`.

**Data seeding: self-seed, self-test.** Log in if needed (credentials from SUMMARY/CONTEXT; seed admin `admin`; if "change password on first login" appears, walk it and note the new password). Create prerequisite institutions / apps / scenes / templates / tokens via API or UI. Data may chain across cases or be seeded per case — your call, but the `note` must stay traceable.

## E4 — Web E2E (Playwright MCP)

`browser_navigate` to the target (`:3000`, `/console`, `/login`) → `browser_snapshot` (a11y tree) → `browser_click`/`browser_type`/`browser_fill_form`/`browser_select_option` → `browser_wait_for` on anything async (**no blind sleep**) → `browser_snapshot` again to verify text, lists and toasts, `browser_console_messages` for JS errors, `browser_network_requests` for API responses; `browser_take_screenshot` only to diagnose a failure; `browser_close` at the end.

**Retry cap: 10 ops per step or case.** Exhausted → mark `blocked`, note where it stuck, and move on.

Playwright MCP unavailable → mark all web steps/cases `blocked` with `note: "Playwright MCP not ready — 需人工验收"`. **Don't downgrade to reading code and guessing.**

## E5 — Pure API (curl)

Assert the HTTP status plus the `R` wrapper's `code`/`message`/`data`. Headers: Open API → `x-dap-appkey`+`x-dap-appsecret`; Data API → `x-dap-appkey`+`x-dap-token`; Admin API → session. Check DB/Redis via `mysql`/`redis-cli` against `t_audit_log`, `dap:token:*`, `dap:vc:revoked:*`. Record what was sent, what came back, and whether it matched.

> ⚠️ **Chinese curl — prevent UTF-8 mojibake** (shell-inline Chinese JSON double-encodes and stores garbage): create `request_file="$(mktemp)"`, `Write` the body into that UTF-8 temp file, then `curl --data @"$request_file" -H 'Content-Type: application/json; charset=UTF-8'`. Read it back via the list/detail API and assert the Chinese fields character by character; any `Ã / Â / å / æ / ç` means mojibake → **stop and report**, don't bulk-write corrupt data.

## E6 — Judgment

- All observable items match → `pass`.
- Any item explicitly doesn't → `issue` for `--uat-autorun` (state expected X / actual Y), `fail` for `--vrf-autorun`.
- Environment or selector stuck with retries exhausted, or a dependency not ready → `blocked`.
- Ran it but still can't judge objectively → `skipped` / `skip` (**don't guess**).

---

## Guardrails

- **Test only, never fix.** Record problems as Gaps or in the report; never change business code, never commit, switch branches, or cut checkpoints.
- **Never release.** Never reply the `<resume-signal>`.
- `--uat-autorun` writes **only the one target UAT file**, and only these fields: `Current Test` / `Tests` `result`+`note`+`severity` / `Summary` / `Gaps` / frontmatter `status`+`updated`. **Never touch `expected`, case titles, or delete cases.** `result` uses only the four native states `pass`/`issue`/`skipped`/`blocked` — never invent `fail`/`skip`.
- `--vrf-autorun` writes **no files**; its report is conversation-only.
- Test data isn't force-cleaned (kept for re-verification); list what was created.
- The report must explicitly surface skips and Gaps — automated verification is not human judgment.
- Reply in Chinese.
