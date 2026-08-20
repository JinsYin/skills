---
name: gsx-plan-phase
description: "Docs-grounded front-door to /gsd:plan-phase that splits its native Research→Plan into two explicitly-gated calls: FIRST a Context7-grounded research pass (/gsd:plan-phase --research-phase N, which spawns gsd-phase-researcher and writes RESEARCH.md) with a MANDATORY Context7 gate — every library/SDK capability, API limit, version difference, framework configuration, DB dialect, or CLI usage the phase relies on is verified against current docs before it lands in RESEARCH.md — THEN the plan pass (/gsd:plan-phase N --skip-research) so gsd-planner builds PLAN.md on top of the grounded research instead of re-deriving from stale assumptions. Use whenever the user wants to plan / create the PLAN.md for a GSD phase — 'plan phase 3', 'plan-phase', 'create the plan for phase X', 'research then plan phase X', 'gsx-plan-phase', or just a phase number in a planning context. Prefer over calling /gsd:plan-phase directly: this guarantees the research feeding the planner is checked against real docs first, because the planner and the executor downstream treat RESEARCH.md as settled and won't re-verify. Passes through plan-phase flags (--tdd, --mvp, --gaps, --skip-verify, --text, etc.)."
argument-hint: "[GSD Phase number] [optional plan-phase flags: --tdd --mvp --gaps --skip-verify --text ...]"
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

# gsx-plan-phase

## Codex Adapter

In Codex, translate this Claude wrapper instead of rewriting it:

- `$ARGUMENTS` = text after `$gsx-*`.
- `/gsd:<name> ...` or `Skill("gsd:<name>", args="...")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options/plans, first print each option's core content in your reply, then list the choices as a numbered Markdown list and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.
- Preserve wrapper boundaries; if GSD owns edits, do not edit source here.


A **docs-grounded** wrapper over `/gsd:plan-phase`. `plan-phase` already runs Research → Plan → Verify internally; this skill makes the boundary between Research and Plan explicit and bolts a Context7 gate onto the research half. It runs the research pass first (producing `{phase}-RESEARCH.md`), enforcing that any fact about *how an external technology actually behaves* is checked against current docs **before** it's written — then hands the grounded research to the planner to produce `{phase}-PLAN.md`.

**Why it exists:** `plan-phase` spawns `gsd-phase-researcher` → `RESEARCH.md`, then `gsd-planner` reads that file as settled input and builds the executable plan from it; `gsd-executor` later implements against the plan. None of the downstream agents re-verify the research. So a single stale assumption baked into `RESEARCH.md` ("MyBatis-Plus supports that join out of the box", "openGauss has `DATE_FORMAT`", "Spring Security's method annotations apply here without extra config", "this API has no payload cap") doesn't just mislead one step — it silently shapes the whole plan and the code that follows. Your training data lags real API / dialect / CLI behavior, and research is the cheapest place to catch a wrong assumption before it compounds. Grounding the *specific* construct the plan will commit to, at research time, is the highest-leverage gate in the whole flow.

**Boundary — this skill never changes code.** It runs research and planning (via `/gsd:plan-phase`) and writes `RESEARCH.md` + `PLAN.md`; it does not edit source, run migrations, or commit anything beyond what `plan-phase` itself does. Implementation belongs to `/gsd:execute-phase` afterward. Reply in Chinese.

---

## 0 — Get the phase number (+ pass-through flags)

`$ARGUMENTS` = the GSD phase number, optionally followed by `plan-phase` flags (`--tdd`, `--mvp`, `--gaps`, `--skip-verify`, `--text`, `--prd`, …). If no phase number is present, ask: *"要为哪个 Phase 做计划？给我 Phase 编号。"* and wait.

Keep any flags the user passed — they belong to the **plan** pass (Step 2) and must reach it unchanged.

**Gap-closure short-circuit:** if `--gaps` is present, the user is closing verification gaps, not planning fresh. `plan-phase --gaps` reads `VERIFICATION.md` and skips research by design, so there's nothing for the research pass to ground. Skip Step 1 entirely and go straight to Step 2 with `--gaps` (do **not** add `--skip-research`; let gap mode run as-is).

## 1 — Research pass: Context7-grounded `RESEARCH.md`

Hand control to `plan-phase` in **research-only mode** so it spawns `gsd-phase-researcher`, writes `{phase}-RESEARCH.md`, and exits before the planner. The researcher carries Context7 tools, so the gate fires *inside* the research — your job is to attach the discipline so grounding happens before any external-behavior claim is recorded.

**The gate triggers whenever a research claim turns on external behavior:**

- **Library / SDK capability** — whether an API exists, what it returns, a default, a documented limit, a method signature.
- **API limit / quota / contract** — rate limits, payload caps, auth requirements, pagination rules of an upstream or third-party API.
- **Version differences** — behavior that differs across versions; a deprecation or breaking change.
- **Framework configuration** — Spring Boot / MyBatis-Plus (incl. mybatis-plus-join) / Spring Security or Sa-Token (whichever this project uses) / Spring Cloud Gateway property, annotation, auto-config, lifecycle.
- **Database dialect** — a function/syntax in MySQL but not openGauss (or vice-versa). This project ships **both** dialects (Flyway double-path), so dialect-dependent claims always get grounded — dialect mismatches are a recurring trap here.
- **CLI / tool usage** — a command flag or subcommand the plan would rely on.

**When the claim is purely internal** (own business rules, naming, scope boundaries, sequencing that doesn't depend on any external API) → no Context7 needed; the researcher proceeds normally.

**How to consult** (per the global Context7 rule): `mcp__context7__resolve-library-id` with the library/framework name + the question → pick the best-matching `/org/project` ID → `mcp__context7__query-docs` with the *full* question, not a single keyword. If the MCP tools aren't reachable, invoke the `context7-mcp` skill. Ground the **exact** construct the plan will commit to (the real method signature, the actual property name, the documented limit, whether the dialect function exists), and record what the docs confirmed alongside the claim in `RESEARCH.md`.

Invoke the research pass with the phase number and **this verbatim constraint block** appended:

```
Skill("gsd:plan-phase", args: "--research-phase <phase-number> --research 【Context7 文档门禁】写 RESEARCH.md 时，凡是某个结论取决于外部技术的真实行为——库或 SDK 能力、API 限制/配额/契约、版本差异、框架配置（Spring Boot / MyBatis-Plus 含 mybatis-plus-join / Spring Security 或 Sa-Token，以本项目实际所用为准 / Spring Cloud Gateway）、数据库方言（MySQL vs openGauss，本项目双方言）、CLI 用法——必须先用 Context7 查证当前文档（resolve-library-id 选 /org/project，再 query-docs 传完整问题，而非单个关键词；MCP 不可用时调用 context7-mcp skill），把计划将要依赖的那个具体构造（真实方法签名 / 属性名 / 文档化的限制 / 方言函数是否存在）核对清楚，再把该结论写进 RESEARCH.md，并在结论旁注明文档确认了什么。纯内部结论（业务规则、命名、范围边界、不依赖外部 API 的时序）无需查 Context7，按常规调研即可。研究完成即退出，不要进入 planner。")
```

Keep the constraint text exactly as written. `--research-phase` forces research-only (exits before the planner) and `--research` forces a fresh pass even if `RESEARCH.md` already exists — so the grounding actually runs rather than reusing a possibly-stale file. Let the researcher own the research structure and the `RESEARCH.md` template; don't draft it yourself.

If the researcher surfaces a tech-shaped claim and you can see the grounding didn't happen, that's your cue to consult Context7 right then (you have the tools) before the plan pass consumes it — don't let it pass.

## 2 — Plan pass: build `PLAN.md` on the grounded research

Now run the planner on top of the just-grounded `RESEARCH.md`. Pass `--skip-research` so `plan-phase` goes straight to the planner (and its verify loop) instead of re-researching, plus any flags the user gave in Step 0:

```
Skill("gsd:plan-phase", args: "<phase-number> --skip-research <any pass-through flags>")
```

Let `plan-phase` own the planner spawn, the `gsd-plan-checker` verification loop, iteration to pass, and the `PLAN.md` write. Don't pre-empt it by drafting tasks yourself.

(For `--gaps` runs you skipped Step 1 — here invoke `plan-phase <phase-number> --gaps <other flags>` without `--skip-research`, since gap mode handles research-skipping itself.)

## 3 — Close out

`plan-phase` produces `{phase}-PLAN.md` (after `{phase}-RESEARCH.md`) and tells the user the next step (usually `/gsd:execute-phase`). Don't re-summarize the whole plan — frame the docs-grounded result:

```
## gsx-plan-phase — Done
Phase {N}：研究 + 计划完成，已写入 {N}-RESEARCH.md、{N}-PLAN.md
Context7 核对：{一行 — 哪些库/API/版本/方言/CLI 结论经文档确认；若研究中全是内部结论则写"本次研究均为内部结论，未涉及外部行为"}
下一步（建议先评审）：/gsx-plan-review {N} — 用外部 Codex CLI 做跨 AI 计划评审，独立挑出假设漏洞 / 缺失边界 / 排序问题，再决定是否执行
下一步（或直接执行）：见上方 plan-phase 的提示（通常是 /gsd:execute-phase {N}）
```

把 `/gsx-plan-review` 摆在执行之前推荐：刚写完计划时，规划者和你都对自己的盲点不敏感，一个独立外部模型冷读计划最能在「写代码前、错误还便宜」的时点发现问题。评审产出 `REVIEWS.md` 后，可用 `/gsx-replan-phase {N}` 把意见回灌进计划——构成 计划 → 评审 → 重规划 的收敛环。

If the run bailed before `PLAN.md` was written (e.g. the verify loop didn't converge, or the user stopped after research), say so plainly and name what *did* land (`RESEARCH.md` only, or nothing).

---

## Guardrails

- **Context7 is not optional when external behavior decides a research claim.** A library capability / API limit / version difference / dialect / CLI question gets grounded in current docs *before* it's written into `RESEARCH.md` — because the planner and executor downstream treat the research as settled and won't re-verify, a stale claim here shapes the whole plan and the code that follows. Skipping is only valid for purely-internal claims.
- **Ground the exact construct, not the topic.** Querying "MyBatis-Plus" in general isn't the gate — confirm the specific method / property / limit / dialect-function the plan will commit to. That's where the lag bites.
- **Research first, then plan — don't collapse them.** The whole point is that the planner consumes *grounded* research. Run Step 1 to completion (fresh, docs-checked `RESEARCH.md`) before Step 2. The two passes are deliberate: `--research-phase` exits before the planner, `--skip-research` starts at the planner.
- **Don't re-implement plan-phase.** Research structure, the planner, the `gsd-plan-checker` verify loop, and both file templates live in `/gsd:plan-phase`. This skill sequences the two passes and adds the gate; it doesn't draft `RESEARCH.md` or `PLAN.md` itself.
- **`--gaps` skips the research pass.** Gap closure reads `VERIFICATION.md` and has no fresh research to ground — go straight to the plan pass in gap mode.
- **No code changes here.** This is a research + planning skill. Implementation belongs to `/gsd:execute-phase` afterward.
- **One phase per run.** A different phase → restart.
