---
name: gsx-debug
description: "Diagnose-first debugging front-door: run /gsd:debug --diagnose to get a root-cause report (diagnose only, no fix), then — whenever the root cause touches library behavior, version differences, framework configuration, or CLI usage — MANDATORY-consult Context7 for current docs before proposing anything, produce one or more concrete fix plans with trade-offs, and finally interview the user twice: which plan to adopt, and which fix path — Quick fix (hands off to the gsx-quick skill) or Manual fix (gsx-debug applies the edits itself and verifies on the running instance). Use whenever the user reports a bug/error/500/stack trace/unexpected behavior and wants it diagnosed and fixed — 'debug this', 'why is X failing', 'this endpoint returns 500', 'diagnose then fix', 'gsx-debug', or pastes an error. Prefer over calling /gsd:debug directly: this adds the Context7 grounding gate and the plan→interview→route loop on top. vs gsx-quick: that runs /gsd:quick --discuss on a problem whose cause is already understood (its discussion settles scope, not root cause); this diagnoses an unknown root cause and grounds it in docs FIRST, then may delegate to gsx-quick for the Quick-fix path."
argument-hint: "[problem description / error / symptom]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Skill
  - AskUserQuestion
  - WebFetch
  - WebSearch
  - mcp__plugin_context7_context7__resolve-library-id
  - mcp__plugin_context7_context7__query-docs
---

# gsx-debug

## Codex Adapter

In Codex, translate this Claude wrapper instead of rewriting it:

- `$ARGUMENTS` = text after `$gsx-*`.
- `/gsd:<name> ...` or `Skill("gsd:<name>", args="...")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options/plans, first print each option's core content in your reply, then list the choices as a numbered Markdown list and **stop and wait** for the user's text reply (see step 4). Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.
- Preserve wrapper boundaries; if GSD owns edits, do not edit source here.


Diagnose → ground-in-docs → plan → choose → fix. One loop that takes a reported symptom from "something's broken" to a landed fix, without guessing.

**Why it exists:** Jumping straight to a fix is how you fix the *symptom* and miss the *cause*. And even with the right cause, a fix written from memory of how a library/framework "probably" behaves is how you ship a second bug. This skill forces two disciplines before any code moves: (1) a scientific root-cause diagnosis via `/gsd:debug --diagnose`, and (2) a Context7 docs check whenever the cause is about *how some external thing actually behaves* — because your training data lags real API/dialect/CLI behavior, and a debug fix is exactly where that gap bites.

**Boundary — diagnosis never fixes.** The `/gsd:debug --diagnose` step is read-only investigation; it produces a Root Cause Report and stops. gsx-debug then decides the fix *with* the user. The Quick-fix path is owned end-to-end by the `gsx-quick` skill (it runs `/gsd:quick --discuss`). The Manual-fix path is the only place gsx-debug itself edits source. Reply in Chinese.

---

## 0 — Get the symptom

`$ARGUMENTS` = the bug / error / symptom. If empty, ask: *"出什么问题了？把现象、报错、复现路径说一句，我先诊断根因再修。"*

Capture whatever the user gives — error text, HTTP status, stack trace, the page/endpoint, what they expected vs saw. The richer this is, the better the diagnosis; don't pad it with guesses.

**Tier check (don't force-fit):**
- If the user already *knows* the root cause and just wants it changed (no investigation needed) → tell them `gsx-quick` / `gsx-fast` fits better and stop unless they still want a diagnosis.
- If it's a sprawling multi-subsystem failure that needs a real investigation campaign → `/gsd:debug` (full, multi-cycle, with fix) may fit better; offer it, let the user confirm.
- Otherwise (a concrete bug worth root-causing before touching) → continue. This is the sweet spot.

## 1 — Diagnose the root cause (`/gsd:debug --diagnose`)

First check whether a diagnosed session already covers this symptom — re-running diagnosis on a known cause wastes a cycle:

```bash
ls .planning/debug/*.md 2>/dev/null | grep -v resolved
```

- A note whose `trigger:` / symptoms clearly match this symptom and whose `status:` is `diagnosed` → **reuse it**; read it and skip to step 2. Tell the user you're reusing the existing diagnosis.
- Otherwise → run a fresh diagnosis:

```
Skill("gsd:debug", args="--diagnose " + symptom)
```

`/gsd:debug --diagnose` runs the scientific-method investigation in its own context and writes `.planning/debug/<slug>.md` (`mode: diagnose_only`, `status: diagnosed`) — a Root Cause Report with hypothesis, confirming evidence, falsification test, and a `fix_rationale`. **It does not apply a fix.** Let it drive; don't interfere.

When it returns, read the report file and pull out: the **confirmed root cause**, the **evidence**, and the **affected code** (file:line, the offending call/config). You need these concrete anchors for the next two steps.

## 2 — Context7 grounding gate (mandatory when external behavior is implicated)

Look at the root cause and classify it. **If the cause is about how some external thing behaves**, you MUST consult Context7 before proposing a fix — no exceptions, no "I'm pretty sure". Triggers:

- **Library / SDK behavior** — a method does/doesn't do what was assumed, a default changed, an option is misused.
- **Version differences** — behavior differs across versions; a deprecation/removal; a breaking change.
- **Framework configuration** — Spring Boot / MyBatis-Plus / Spring Security or Sa-Token (whichever this project uses) / Spring Cloud Gateway property, annotation, auto-config, lifecycle.
- **Database dialect** — a function/syntax exists in MySQL but not openGauss (or vice-versa), e.g. `HOUR()` / `DATE_FORMAT()` → openGauss has no such function. (This project runs both — dialect mismatches are a recurring root-cause class.)
- **CLI / tool usage** — a command flag, subcommand, or config the fix would rely on.

**Ground every implicated technology, not just the loudest one.** A root cause usually surfaces *one* external thing (here: the openGauss dialect rejecting `HOUR()`), but the fix edits code that lives inside *another* (here: a MyBatis-Plus `@Select` mapper, with mybatis-plus-join in the project). Before consulting, **enumerate the full set**: the technology named in the cause ∪ the framework/library/SDK of the code you'll actually change. Consult each — the framework you're editing often offers a cleaner, officially-supported way to do the fix, or imposes a constraint that rules out your first idea. (Real example: MyBatis-Plus's docs show the supported multi-dialect mechanism is XML `databaseId` / `_databaseId` — but this project is *no-XML*, so that path actually requires `@SelectProvider`, not a "dual `@Select`" you'd otherwise guess wrong; and mybatis-plus-join's `selectFunc` only passes the function string through, so it gives no dialect portability. You only learn both by querying MP/MPJ docs, not just openGauss.) Skipping the framework-of-the-edit is the most common way this gate half-fires.

**How to consult** (per the global Context7 rule): call the Context7 MCP — `resolve-library-id` with the library/framework name + the question → pick the best-matching `/org/project` ID → `query-docs` with the full question (not a single keyword). (Tool names are environment-specific, e.g. `mcp__plugin_context7_context7__resolve-library-id` / `…__query-docs`; use whichever Context7 MCP tools are present.) Ground the *exact* construct the fix will use (the replacement function, the correct property name, the current method signature) against current docs — that's the whole point.

**Fallback ladder if the MCP isn't reachable in this context** (e.g. a subagent without the MCP wired in): (1) invoke the `context7-mcp` skill; (2) if that's also unavailable, degrade to the **official docs** via `WebFetch`/`WebSearch` — the project library's own documentation site, not a random blog. This is a *degraded grounding*, not a skip: you still verified against real docs, so say so and cite the URL. Only a purely-internal cause justifies grounding nothing.

**If the cause is purely internal** (own business logic, a null-check, a wrong conditional, a typo, local state) → no external API is in question, so skip Context7 and go to step 3. State briefly why you skipped it so the user sees it was a decision, not an omission.

Write what Context7 confirmed (or that you skipped it and why) **explicitly in the conversation** — this grounding is the distinctive value of the skill; make it visible.

## 3 — Produce the fix plan(s)

Turn the grounded root cause into **one or more concrete fix options**. Real bugs often have a quick-targeted fix and a more-correct-but-broader fix — surface both so the user can choose the altitude. For each option give:

- **What changes** — the actual file(s) / function / config and the concrete change (name the replacement call, property, query rewrite — grounded by step 2, not hand-wavy).
- **Scope & risk** — how many files, does it touch backend / DB / migration, blast radius, what could regress.
- **Trade-off** — why pick this over the other (e.g. *"局部替换 `HOUR()`→`EXTRACT(HOUR FROM …)` 最小改动，但只治这一处；抽象方言层根治但动 3 个 Mapper"*).

If there's genuinely only one sensible fix, say so and present the single plan — don't manufacture fake alternatives.

## 4 — Interview: which plan + which fix path

Ask **two questions** and wait for the user's answer before routing. The *content* is fixed; only the *mechanism* adapts to the harness — never assume `AskUserQuestion` exists.

**First print the plans, then ask — regardless of mechanism.** Before posing question 1, write each candidate plan's *core content* into the conversation (its **What changes / Scope & risk / Trade-off** from step 3), so the user decides on substance, not a one-word picker label. A terse option label alone is not enough — the plan body must be visible right above the choice.

**How to ask:**
- **Interactive question tool available** (Claude Code's `AskUserQuestion`, or a Codex build where `request_user_input` actually renders an interactive picker) → print the plan bodies first (above), then batch both questions into one round, one option per choice. Preferred where supported.
- **No interactive question tool** (e.g. running under **Codex**, where `AskUserQuestion` can't conduct an interactive interview) → **do NOT call `AskUserQuestion` / `request_user_input`** — it won't prompt the user, and you must not self-answer a prompt the user never saw. Instead write both questions as a plain **numbered Markdown list** in your reply, label every option so the user can answer compactly (e.g. *"1: 方案 B，2: Quick fix"*), then **stop and wait** for their text reply. Resume routing only after they answer.

**The two questions (same either way):**
1. **修复方案** — one entry per fix plan from step 3: the plan's one-line essence + its scope/trade-off. If there's only one plan, still present it and ask for a confirm-or-adjust.
2. **修复方式** — exactly two options:
   - `Quick fix（gsx-quick）` — hand the chosen plan to the `gsx-quick` skill (`/gsd:quick --discuss`: 讨论 + 研究 + 计划校验 + 执行 + 验证). Best when it touches backend/DB or you want the structured, atomic, reversible flow.
   - `Manual fix` — gsx-debug applies the edits itself and verifies on the running instance. Best for a small, well-contained change you want done in place now.

Respect the answers. If the user picks a plan but wants to tweak it (their own text), fold that into the chosen plan before routing.

## 5 — Route the fix

### 5a — Quick fix → hand off to gsx-quick

Compose the chosen, grounded plan into one clear task statement (carry the root cause, the concrete change, the file:line anchors, any backend/DB touch, and what Context7 confirmed), then:

```
Skill("gsx-quick", args=<composed fix task from the chosen plan>)
```

`gsx-quick` now fully owns the run — the whole `/gsd:quick --discuss` pipeline. **Do not interfere or re-plan.** Your diagnosis established *what's wrong and why*; its discussion round settles *how to change it*. Complementary, not redundant — hand the root cause over and let it drive. When it returns → step 6.

### 5b — Manual fix → gsx-debug applies + verifies

This is the only place gsx-debug edits source. Apply the chosen plan with Edit/Write, scoped tightly to the root cause — don't drift into unrelated cleanup.

Then **verify on the running instance — do not claim fixed from a clean compile alone.** This project runs `spring-boot:run` without devtools, so a recompile isn't picked up live; you must rebuild and restart the affected service, then reproduce the original symptom and confirm it's gone:

- Backend change → recompile, then restart the affected service via the project's process-compose socket (e.g. `process-compose process restart dap-admin -u <sock>`); if `dap-common` changed, it's the stale-jar trap — rebuild common and restart consumers.
- Then re-trigger the exact failing path (the endpoint/page/command from the symptom) and confirm the 500 / error / wrong behavior is gone. Prefer a real request over a hand-built one.

Show the user the diff and the verification result (the now-passing request/output). If verification fails, say so plainly with the output — don't paper over it; loop back to step 3 with what you learned.

## 6 — Close out

- **Mark the debug note resolved** — update the `.planning/debug/<slug>.md` frontmatter `status:` to `resolved` and `updated:` to today, so it drops out of the active-session list. (Quick-fix path: do this after `gsx-quick` lands its commit; Manual-fix path: after verification passes.)
- **Final summary:**

```
## gsx-debug — Done
根因：{one-line confirmed root cause} （见 .planning/debug/{slug}.md）
Context7：{what current docs confirmed, or "未涉及外部行为，已跳过"}
方案：{chosen plan one-liner}
修复方式：{Quick fix — 见上方 gsx-quick close-out / Manual fix — {commit or diff}，已在运行实例验证：{the passing request/output}}
```

If the user bailed during the interview (chose neither path, or it turned out to be a known cause needing only gsx-quick), say so plainly — no fix landed, nothing committed.

---

## Guardrails

- **Diagnose before fixing, always.** The value is root-cause-first. Don't let a confident-looking symptom tempt you into skipping `/gsd:debug --diagnose`.
- **Context7 is not optional when external behavior is implicated.** Library/version/framework/dialect/CLI causes get grounded in current docs before the plan — your memory of an API is exactly what a debug fix can't rely on. Skipping is only valid for purely-internal causes, and you must say why.
- **Don't pre-empt gsx-quick's discussion round.** On the Quick-fix path, flag backend involvement in the handoff but leave the concrete endpoint→Controller→VO plan and its confirmation to `gsx-quick` / `/gsd:quick --discuss`.
- **Manual fix = verify on the running instance.** A clean compile is not a fix here. Restart and reproduce, or it isn't done.
- **One bug per run.** A different symptom → restart. No branch switching.
