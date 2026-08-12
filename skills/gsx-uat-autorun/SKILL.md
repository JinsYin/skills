---
name: gsx-uat-autorun
description: "Auto-run every test case under `## Tests` of a GSD Phase's HUMAN-UAT.md / UAT.md and write results back live — background tasks for cold-start smoke, Playwright MCP for web E2E, curl for APIs, self-seed and test; set each result (pass/issue/skipped/blocked) + note, skip undecidable ones with a reason, update Summary, write Gaps into `## Gaps`. Test only, never fix. Arg is the Phase number (inferred from context/STATE.md if blank). Invoke: 'auto-test UAT', 'auto-run Phase X's test cases', 'autorun', 'gsx-uat-autorun'."
argument-hint: "[Phase #, e.g. 4 / 04 / Phase 4; inferred from context/STATE.md if blank]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
  - Agent
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_navigate_back
  - mcp__playwright__browser_snapshot
  - mcp__playwright__browser_click
  - mcp__playwright__browser_type
  - mcp__playwright__browser_fill_form
  - mcp__playwright__browser_select_option
  - mcp__playwright__browser_press_key
  - mcp__playwright__browser_hover
  - mcp__playwright__browser_wait_for
  - mcp__playwright__browser_take_screenshot
  - mcp__playwright__browser_console_messages
  - mcp__playwright__browser_network_requests
  - mcp__playwright__browser_evaluate
  - mcp__playwright__browser_handle_dialog
  - mcp__playwright__browser_tabs
  - mcp__playwright__browser_close
---

# gsx-uat-autorun

## Codex Adapter

In Codex, translate this Claude wrapper instead of rewriting it:

- `$ARGUMENTS` = text after `$gsx-*`.
- `/gsd:<name> ...` or `Skill("gsd:<name>", args="...")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options/plans, first print each option's core content in your reply, then list the choices as a numbered Markdown list and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.
- Preserve wrapper boundaries; if GSD owns edits, do not edit source here.
- **Subagent delegation (§2.5)**: if your Codex build has no subagent/`Agent` equivalent, skip §2.5 and run §3–§5 inline in the same context. The token-saving split is a Claude优化，not a correctness requirement.


Automated runner for `/gsd:verify-work`. Writes back the **same UAT file, same fields**, using native status words `pass`/`issue`/`skipped`/`blocked` (for verify-work continuation + `/gsd:plan-phase --gaps`).

**Boundary:** Test only, never fix — bug → `## Gaps`, never change business code (fixes → `/gsd:quick` / `/gsd:debug`). Write back, never create — only update an existing UAT file; absent → tell user to run `/gsd:verify-work {NN}` first. No commits/branch switching/checkpoints. Test data self-managed, not force-cleaned (kept for re-verification), noted in `note`.

---

## Execution model — Opus 编排，Sonnet 子代理执行

为最大化节省主线程（Opus）token，本 skill 把**轻量编排**与**重量执行**分离：

- **编排（主线程 / Opus）**：§0–§2 解析 Phase、定位并解析 UAT、分类用例、展示计划表；§2.5 起**一个 Sonnet 子代理**承接执行；§6 把子代理回传的精简摘要呈现给用户。
- **执行（子代理 / Sonnet）**：§3–§5 冷启动、逐用例跑 Playwright/curl、回写 UAT 文件、收尾。所有冗长工具输出（a11y 快照、`browser_network_requests`、curl 响应全文、冷启动日志 tail）都留在子代理上下文，主线程只见到计划表和最终摘要——既省 token，单价又更低。

子代理用 `general-purpose` 类型（自带 Bash 后台任务、Playwright MCP、Read/Write/Edit 全量工具）、`model: "sonnet"`。它直接回写磁盘上的**真实** UAT 文件，因此实时进度与「可中断—续跑」能力依旧保留。

---

## 0 — Parse Phase number

Phase dirs: `.planning/phases/{NN}-{slug}/`, `NN` zero-padded to 2 digits.

- `$ARGUMENTS` has a number → normalize (ignore case, `Phase` prefix, spaces): `4`/`04`/`Phase 4` → `04`.
- Blank → infer: (1) Phase under discussion; (2) else STATE.md `Last completed phase` (or `Active phase` if tone says "test current phase"); (3) ambiguous → `AskUserQuestion`, don't guess.
- No `.planning/` → not a GSD project; tell user and stop.

## 1 — Locate and parse the UAT file

```bash
ls .planning/phases/{NN}-*/{NN}-*UAT.md
```

- 0 matches → "Phase {NN} has no HUMAN-UAT.md / UAT.md — run `/gsd:verify-work {NN}` first." Stop.
- Multiple (UAT + HUMAN-UAT) → prefer `HUMAN-UAT.md`; note which selected / left untouched.

Parse the verify-work structure: **frontmatter** (`status`/`phase`/`started`/`updated`); **`## Current Test`** (`number`/`name`/`expected`/`awaiting`); **`## Tests`** (`### N. <title>` + `expected:` + `result:`); **`## Summary`** (`total`/`passed`/`issues`/`pending`/`skipped`/`blocked`); **`## Gaps`** (YAML for failing cases).

Extract each case's **N**, **title**, **expected**. Existing `result` is reference only — re-run all cases independently (incl. manually-marked; actual results win). Also read `{NN}-CONTEXT.md` / `{NN}-*-SUMMARY.md` / `{NN}-PLAN.md` for APIs/pages, credentials + initial data, env prerequisites. Root `CLAUDE.md` "Local Run" = authoritative cold-start guide.

## 2 — Classify each case

| Category | Signals (expected/title) | Execution |
|----------|---------------------------|-----------|
| **Cold-start smoke** | cold-start / docker-compose / service up / Flyway migration / startup logs | Step 3: **background tasks**, confirm readiness |
| **Web E2E** | UI behavior: page/console/list/drawer/button/click/toast/form validation | **Playwright MCP** |
| **Pure API** | HTTP contract: error codes, response fields, headers, `/openapi/*`, `/admin/*`, DB persistence | **curl** (+ `mysql`/`redis-cli`) |
| **Skip** | see below | `result: skipped` |

**Skip when can't machine-determine:** subjective with no objective anchor (color/badge tint, "matches prototype", polish, layout feel); prerequisite not self-buildable (real DID SDK, real upstream API, prod deploy/monitoring/backup, external third-party); expected too vague (no observable success criterion); mixed-subitem case — run coverable part, mark rest "partially skipped" in `note`. When in doubt, **prefer skip** (reason in `note`).

Show a brief plan table (number/title/category), then go to §2.5.

## 2.5 — 起 Sonnet 子代理执行

**先在主线程处理需要用户交互的前置项**（子代理不便弹交互）：若存在冷启动用例且其 `expected` 要求「重置 DB / 删除 `docker/mysql|redis/data`」这类破坏性操作，**现在就 `AskUserQuestion` 确认**；用户拒绝则把该决定传入子代理，由其将相关用例标 `skipped`、`note: "DB reset required — not authorized."`。

然后用 `Agent` 起**一个** Sonnet 子代理执行 §3–§5。prompt 至少包含：

- **执行协议（单一事实来源，勿在 prompt 复述）**：`阅读 .claude/skills/gsx-uat-autorun/SKILL.md 的 §3、§4、§5 与「## Guardrails」，严格按其执行`。
- **目标 UAT 文件绝对路径**（§1 选中的那个，如 `.planning/phases/04-xxx/04-HUMAN-UAT.md`）；提示「只回写这一个文件」。
- **Phase 号 + phase 目录**，及要读的上下文文件（`{NN}-CONTEXT.md` / `{NN}-*-SUMMARY.md` / `{NN}-PLAN.md`、根 `CLAUDE.md` 的「本地运行」）。
- **分类计划**：每个用例的 N / 标题 / 类别（cold-start / web / api / skip），即 §2 的计划表。
- **破坏性操作决定**：上面 AskUserQuestion 的结果。
- **回传要求（关键，省 token）**：只回传精简摘要——最终 Summary 计数、skipped/blocked 列表（各带一句原因）、Gap 列表（issue 用例）。**严禁**把 Playwright 快照、`browser_network_requests`、curl 全文、日志贴回主线程。

调用形如 `Agent(subagent_type="general-purpose", model="sonnet", description="autorun Phase NN", prompt=<上述>)`。子代理的「只测不修 / 只回写目标 UAT / result 只用四态」边界在它阅读 §3–§5 + Guardrails 时即已加载，无需在 prompt 重述。

> Playwright MCP 是单浏览器实例：同一时刻只起**一个**子代理跑 web 用例，勿并行起多个争抢浏览器。
> 子代理跑完后跳到 §6 呈现。

---

> **以下 §3–§5 是「执行协议」，在 §2.5 起的 Sonnet 子代理上下文里运行**（无子代理的 Codex 场景下则内联运行）。

## 3 — Prepare environment (cold-start)

**Probe first** (all cases need services online): `curl -s -o /dev/null -w "%{http_code}"` on :8080 and :3000.

**If there are cold-start smoke cases**, the stack must start from stopped. **Stop first**: `docker-compose down` (no `-v` — keep volumes), kill running backend/frontend bg processes. Then follow `CLAUDE.md` "Local Run" via background tasks (`run_in_background`):

1. `docker-compose up -d` (MySQL 5.7 + Redis 7).
2. `cd dap-server && mvn -pl dap-common install -DskipTests` (foreground wait; latest dap-common → `~/.m2`).
3. `mvn -pl dap-admin spring-boot:run` — bg (:8080); also `dap-gateway` (:8090) / `dap-transform` (:8091) if tested. **`spring-boot:run` can't use `-am`; run under `dap-server/`.**
4. `cd dap-frontend && pnpm install && pnpm dev` — bg (:3000).
5. Poll: `curl` each port until it responds; logs confirm Flyway done, no real `ERROR` (benign macOS netty DNS warnings don't count).

> ⚠️ Destructive ops: cold-start `expected` requiring "reset DB / delete `docker/mysql/data` or `docker/redis/data`" 的授权**已由编排层在 §2.5 预先确认并随 prompt 传入** —— 授权则执行；未授权 → `result: skipped`, `note: "DB reset required — not authorized."`（子代理勿自行再弹交互）。Local JDK must be 21; on version error switch `JAVA_HOME` per CLAUDE.md.

Services fail / migration errors → cold-start cases `result: issue` + log excerpt in `note`; dependent cases `result: blocked`, `note: "environment unavailable"`; stop trying.

## 4 — Run each case and write back

Run in sequence order. **Each case: update Current Test → execute → write back result + note → update Summary**, then next. Per-case writes give real-time progress + interruptible-resumable state.

**4.0 — Update Current Test** — `Edit` `## Current Test` to `number: N` / `name: <case title>` / `expected: |` (verbatim) / `awaiting: autotest running`.

**4.1 — Seed and execute** — self-seed, self-test. Login if needed (credentials from SUMMARY/CONTEXT; seed admin `admin`; "change password on first login" → walk it, note new password). Create prerequisite institutions/apps/scenes/templates/tokens via API or UI. Data may chain across cases or seed per case — your call, but `note` must be traceable.

- **Cold-start smoke** — start stack per step 3; verify each expected item (migration version, table count, seed data, port accessibility, key pages load); record actual values.
- **Web E2E (Playwright MCP)** — `browser_navigate` → `browser_snapshot` (a11y tree) → `browser_click`/`browser_type`/`browser_fill_form`/`browser_select_option` → `browser_wait_for` on async (no blind sleep) → `browser_snapshot` to verify text/list/toasts, `browser_console_messages` for JS errors, `browser_network_requests` for API responses; `browser_take_screenshot` only to diagnose; `browser_close` at end. **Retry cap = 10 ops/case** — exhausted → `result: blocked`, note the stuck step, move on. Playwright MCP unavailable → all web cases `result: blocked`, `note: "Playwright MCP not ready — needs manual acceptance"`; don't downgrade to reading code and guessing.
- **Pure API (curl)** — assert HTTP status + `R` wrapper `code`/`message`/`data`. Open API: `x-dap-appkey`+`x-dap-appsecret`; Data API: `x-dap-appkey`+`x-dap-token`; Admin API: session. DB/Redis via `mysql`/`redis-cli` on `t_audit_log`, `dap:token:*`, etc.

> ⚠️ **Chinese curl — prevent UTF-8 mojibake** (shell-inline Chinese JSON double-encodes and stores garbage): create `request_file="$(mktemp)"`, `Write` the body to that UTF-8 temp file, then `curl --data @"$request_file" -H 'Content-Type: application/json; charset=UTF-8'`. Read back via list/detail API, assert Chinese fields char-by-char; any `Ã / Â / å / æ / ç` → mojibake → **stop and report**, don't bulk-write corrupt data.

**4.2 — Judge** — all observable items match → `pass`; any explicitly doesn't → `issue`; env/selector stuck + retries exhausted or dependency not ready → `blocked`; can't objectively judge after running → `skipped`.

**4.3 — Write back this case** — `Edit` the case block in `## Tests` (anchor on `### N. <title>`). **Every case writes both `result` and `note`** (one-line evidence): `pass` → "what tested, what observed"; `issue` → add `severity` line + "expected X, actual Y"; `skipped` → skip reason; `blocked` → blocking point + env reason. Example:
```
### 10. 全链路审计落库
expected: 请求后 t_audit_log 落 1 条含 log_type/latency_ms/...
result: issue
severity: major
note: 1 个请求落 2 条审计记录（id 28/29 内容相同），审计重复写入
```

`severity` (when `issue`; from actual consequence, don't ask): crash/exception/unavailable → `blocker`; wrong behavior/missing feature → `major`; deviates/intermittent/slow → `minor`; purely visual → `cosmetic`.

**4.4 — Update Summary** — after each case, `Edit` `## Summary` (`total` unchanged; `passed`/`issues`/`skipped`/`blocked` accumulate; `pending` = cases not yet run) and bump frontmatter `updated`. Return to 4.0 for next.

## 5 — Close-out

1. **`## Current Test`** → `[autotest complete]`.
2. **`## Summary`** → confirm counts match (pending = 0).
3. **frontmatter `status`** → no `pending`/`blocked` → `complete`; some `blocked` → `partial`. Bump `updated`.
4. **`## Gaps`** → append each `result: issue` case as verify-work YAML (`blocked`/`skipped` do NOT become Gaps — env/judgment, not code defects). Fields: `truth` (assertion from expected), `status: failed`, `reason: "Autotest: <expected X, actual Y>"`, `severity` (blocker|major|minor|cosmetic), `test` (case number), `artifacts: []`, `missing: []`. Was `[none yet]`/placeholder → replace; else append.
5. **回传给编排层（精简）**: 子代理把以下作为 final message 返回，**不**贴工具原始输出——最终 Summary 计数（total/passed/issues/skipped/blocked）；**skipped/blocked 列表**（各一句原因，需人工 `/gsd:verify-work {NN}`）；**Gap 列表**（`issue` 用例，修复走 `/gsd:quick` 或 `/gsd:debug`）。

## 6 — 呈现结果（主线程 / Opus）

子代理返回后，编排层无需重跑任何用例，直接把其精简摘要用中文转述给用户：Summary 计数、skipped/blocked 清单（为何需人工复核）、Gap 清单（如何修复）。提醒：结果已实时回写到 `{NN}-*UAT.md`，skipped 项仍需人工 `/gsd:verify-work {NN}` 复核。

## Guardrails

- Write **only the target UAT file**, only fields `Current Test` / `Tests` `result`+`note`+`severity` / `Summary` / `Gaps` / frontmatter `status`+`updated` — never touch `expected`, case titles, or delete cases.
- `result` uses only the four native states `pass`/`issue`/`skipped`/`blocked` — never invent `fail`/`skip`.
- Reply in Chinese.
