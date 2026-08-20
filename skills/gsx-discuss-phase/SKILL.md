---
name: gsx-discuss-phase
description: "Docs-grounded front-door to /gsd:discuss-phase: run the phase-context discussion that produces CONTEXT.md, but with a MANDATORY Context7 gate — whenever a gray area being discussed turns on a technology choice, a library/SDK capability, an API limit, a version difference, framework configuration, a DB dialect, or CLI usage, consult Context7 for current docs BEFORE posing the question or recording the decision, so CONTEXT.md captures grounded facts instead of guesses. Use whenever the user wants to discuss / gather context / make decisions for a GSD phase before planning — 'discuss phase 3', 'discuss-phase', 'gather context for phase X', 'let's decide the tech for this phase', 'gsx-discuss-phase', or just a phase number in a pre-planning context. Prefer over calling /gsd:discuss-phase directly: this adds the Context7 grounding gate so technology-selection / library-capability / API-limit decisions are checked against real docs before they get locked into CONTEXT.md. Passes through discuss-phase flags (--power, --assumptions, --all, etc.)."
argument-hint: "[GSD Phase number] [optional discuss-phase flags: --power --assumptions --all --auto ...]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Skill
  - AskUserQuestion
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
---

# gsx-discuss-phase

## Codex Adapter

In Codex, translate this Claude wrapper instead of rewriting it:

- `$ARGUMENTS` = text after `$gsx-*`.
- `/gsd:<name> ...` or `Skill("gsd:<name>", args="...")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options/plans, first print each option's core content in your reply, then list the choices as a numbered Markdown list and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.
- Preserve wrapper boundaries; if GSD owns edits, do not edit source here.


A **docs-grounded** wrapper over `/gsd:discuss-phase`. It runs the normal phase-context discussion that ends in `{phase}-CONTEXT.md`, but enforces one extra discipline: any gray area whose answer depends on *how some external technology actually behaves* gets checked against current Context7 docs **before** the question is posed or the decision is written down.

**Why it exists:** `discuss-phase` locks decisions into `CONTEXT.md`, and the researcher + planner downstream treat those as settled — they won't re-ask. So a decision made on a stale assumption ("MyBatis-Plus supports that out of the box", "openGauss has `DATE_FORMAT`", "Spring Security / Sa-Token can do X") doesn't just cost this discussion — it silently poisons research and planning. Your training data lags real API / dialect / CLI behavior, and phase discussion is exactly where a technology choice gets fixed. Grounding the *specific* construct in current docs before locking it is the cheapest place to catch a wrong assumption.

**Boundary — this skill never changes code.** It runs a discussion and writes `CONTEXT.md` (via `/gsd:discuss-phase`); it does not edit source, run migrations, or commit anything beyond what `discuss-phase` itself does. Reply in Chinese.

---

## 0 — Get the phase number (+ pass-through flags)

`$ARGUMENTS` = the GSD phase number, optionally followed by `discuss-phase` flags (`--power`, `--assumptions`, `--all`, `--auto`, `--text`, …). If no phase number is present, ask: *"要为哪个 Phase 做讨论 / 收集上下文？给我 Phase 编号。"* and wait.

Keep any flags the user passed — they belong to `discuss-phase` and must reach it unchanged.

## 1 — Set the Context7 gate before handing off

You are about to hand control to `/gsd:discuss-phase`, which drives the adaptive questioning itself. Your job here is to make sure the Context7 discipline holds *inside* that discussion — because gray areas only surface once the workflow analyzes the phase, the grounding can't happen as a separate up-front step. It has to fire the moment a tech-shaped gray area appears, before that question is asked or its answer is recorded.

**The gate triggers whenever a gray area turns on external behavior:**

- **Technology / library selection** — choosing between libraries, or whether a chosen one even *can* do the thing (e.g. "JSONata vs. a custom filter", "does mybatis-plus-join support this join shape").
- **Library / SDK capability** — whether an API exists, what it returns, a default, a documented limit.
- **API limit / quota / contract** — rate limits, payload caps, auth requirements, pagination rules of an upstream or third-party API.
- **Version differences** — behavior that differs across versions; a deprecation or breaking change.
- **Framework configuration** — Spring Boot / MyBatis-Plus / Spring Security or Sa-Token (whichever this project uses) / Spring Cloud Gateway property, annotation, auto-config, lifecycle.
- **Database dialect** — a function/syntax in MySQL but not openGauss (or vice-versa). This project ships both dialects (Flyway double-path) — dialect mismatches are a recurring trap, so dialect-dependent decisions always get grounded.
- **CLI / tool usage** — a command flag or subcommand a decision would rely on.

**When the cause is purely internal** (own business rules, naming, scope boundaries, which fields a scene exposes, a sequencing choice that doesn't depend on any external API) → no Context7 needed; decide it in the normal discussion.

**How to consult** (per the global Context7 rule): `mcp__context7__resolve-library-id` with the library/framework name + the question → pick the best-matching `/org/project` ID → `mcp__context7__query-docs` with the *full* question, not a single keyword. If the MCP tools aren't reachable, invoke the `context7-mcp` skill. Ground the **exact** construct the decision will commit to (the real method signature, the actual property name, the documented limit, whether the dialect function exists), then bring that grounded fact into the question so the user chooses among real options — and record what the docs confirmed in `CONTEXT.md` next to the decision.

## 2 — Hand off to /gsd:discuss-phase with the gate attached

Invoke `discuss-phase` with the phase number, any pass-through flags, **and this verbatim constraint block** appended to the args:

```
Skill("gsd:discuss-phase", args: "<phase-number> <any pass-through flags> 【Context7 文档门禁】在本次讨论中，凡是某个灰区的结论取决于外部技术的真实行为——技术/库选型、库或 SDK 能力、API 限制/配额/契约、版本差异、框架配置（Spring Boot / MyBatis-Plus / Spring Security 或 Sa-Token，以本项目实际所用为准 / Spring Cloud Gateway）、数据库方言（MySQL vs openGauss，本项目双方言）、CLI 用法——必须先用 Context7 查证当前文档（resolve-library-id 选 /org/project，再 query-docs 传完整问题，而非单个关键词；MCP 不可用时调用 context7-mcp skill），把要锁定的那个具体构造（真实方法签名 / 属性名 / 文档化的限制 / 方言函数是否存在）核对清楚，再向我抛出灰区问题、再把决策写进 CONTEXT.md；问题里要给出基于文档的真实选项，CONTEXT.md 中在该决策旁记下文档确认了什么。纯内部决策（业务规则、命名、范围边界、字段取舍、不依赖外部 API 的时序选择）无需查 Context7，按常规讨论即可。")
```

Keep the constraint text exactly as written. Let `discuss-phase` own the questioning, gray-area analysis, mode routing, and the `CONTEXT.md` write — don't pre-empt it by guessing the gray areas yourself or drafting `CONTEXT.md` here. Your only addition is the standing gate.

If the workflow surfaces a tech-shaped gray area and you notice the grounding didn't happen, that's your cue to consult Context7 right then (you have the tools) before that decision is locked — don't let it pass.

## 3 — Close out

`discuss-phase` produces `{phase}-CONTEXT.md` and tells the user the next step (usually `/gsd:plan-phase`). Don't re-summarize the whole discussion — just frame the docs-grounded result:

```
## gsx-discuss-phase — Done
Phase {N}：讨论完成，已写入 {N}-CONTEXT.md
Context7 核对：{一行 — 哪些技术/库/API/方言决策经文档确认；若全是内部决策则写"本次均为内部决策，未涉及外部行为"}
下一步：见上方 discuss-phase 的提示（通常是 /gsd:plan-phase {N}）
```

If the user bailed before `CONTEXT.md` was written, say so plainly — no context file landed.

---

## Guardrails

- **Context7 is not optional when external behavior decides the answer.** A technology choice / library capability / API limit / dialect question gets grounded in current docs *before* it's locked into `CONTEXT.md` — because the researcher and planner downstream won't re-ask, a stale assumption here propagates silently. Skipping is only valid for purely-internal decisions.
- **Ground the exact construct, not the topic.** Querying "MyBatis-Plus" in general isn't the gate — confirm the specific method / property / limit / dialect-function the decision will commit to. That's where the lag bites.
- **Don't re-implement discuss-phase.** Mode routing, gray-area analysis, the question loop, and the `CONTEXT.md` template all live in `/gsd:discuss-phase`. This skill adds the gate and hands off; it doesn't draft `CONTEXT.md` itself.
- **No code changes here.** This is a discussion/decision skill. Implementation belongs to `/gsd:plan-phase` + `/gsd:execute-phase` afterward.
- **One phase per run.** A different phase → restart.
