# `--discuss-phase` / `--plan-phase` — discussion and planning, docs-grounded

Both modes share one idea: bolt the Context7 docs gate (`common.md` §D) onto GSD's discussion/research step, **because nothing downstream re-verifies**. They differ only in which step it's bolted to and which file comes out.

**Boundary — neither mode changes code.** They run discussion / research / planning and write `CONTEXT.md` / `RESEARCH.md` / `PLAN.md`; they don't edit source, run migrations, or commit beyond what `/gsd:*` itself does. Implementation belongs to `/gsd:execute-phase` afterward. Phase inference when the arg is blank: `common.md` §A.

---

## `--discuss-phase` — phase discussion → `CONTEXT.md`

**Why the gate**: `discuss-phase` locks decisions into `CONTEXT.md`, and the researcher and planner downstream treat those as settled — **they won't re-ask**. So a decision made on a stale assumption ("MyBatis-Plus supports that out of the box", "openGauss has `DATE_FORMAT`", "Spring Security / Sa-Token can do X") doesn't just cost this discussion; it silently poisons research and planning. Grounding the specific construct before it's locked is the cheapest place to catch a wrong assumption.

### 0 — Args

Arg = the Phase number, optionally followed by `discuss-phase` flags (`--power`, `--assumptions`, `--all`, `--auto`, `--text`, …). No Phase number → ask *"要为哪个 Phase 做讨论 / 收集上下文？给我 Phase 编号。"* and wait. The user's flags belong to `discuss-phase` and must reach it unchanged.

### 1 — Set the gate, then hand off

You're about to hand control to `/gsd:discuss-phase`, which drives the adaptive questioning itself. Your job is to make the Context7 discipline hold *inside* that discussion — gray areas only surface once the workflow analyzes the phase, so the grounding can't be a separate up-front step. It has to fire the moment a tech-shaped gray area appears, before that question is asked or its answer recorded.

Invoke with the Phase number, any pass-through flags, and this **verbatim** constraint block:

```
Skill("gsd:discuss-phase", args: "<phase-number> <any pass-through flags> 【Context7 文档门禁】在本次讨论中，凡是某个灰区的结论取决于外部技术的真实行为——技术/库选型、库或 SDK 能力、API 限制/配额/契约、版本差异、框架配置（Spring Boot / MyBatis-Plus / Spring Security 或 Sa-Token，以本项目实际所用为准 / Spring Cloud Gateway）、数据库方言（MySQL vs openGauss，本项目双方言）、CLI 用法——必须先用 Context7 查证当前文档（resolve-library-id 选 /org/project，再 query-docs 传完整问题，而非单个关键词；MCP 不可用时调用 context7-mcp skill），把要锁定的那个具体构造（真实方法签名 / 属性名 / 文档化的限制 / 方言函数是否存在）核对清楚，再向我抛出灰区问题、再把决策写进 CONTEXT.md；问题里要给出基于文档的真实选项，CONTEXT.md 中在该决策旁记下文档确认了什么。纯内部决策（业务规则、命名、范围边界、字段取舍、不依赖外部 API 的时序选择）无需查 Context7，按常规讨论即可。")
```

Keep the constraint text exactly as written. Questioning, gray-area analysis, mode routing and the `CONTEXT.md` write all belong to `discuss-phase` — don't pre-empt it by guessing the gray areas or drafting `CONTEXT.md` here. Your only addition is the standing gate.

If the workflow surfaces a tech-shaped gray area and you can see the grounding didn't happen, that's your cue to consult Context7 right then (you have the tools) before that decision is locked — **don't let it pass**.

### 2 — Close out

```
## gsx --discuss-phase — Done
Phase {N}：讨论完成，已写入 {N}-CONTEXT.md
Context7 核对：{一行 —— 哪些技术/库/API/方言决策经文档确认；若全是内部决策则写「本次均为内部决策，未涉及外部行为」}
下一步：见上方 discuss-phase 的提示（通常是 gsx --plan-phase {N}）
```

If the user bailed before `CONTEXT.md` was written, say so plainly — no context file landed.

---

## `--plan-phase` — research then plan, two explicit passes

`plan-phase` already runs Research → Plan → Verify internally; this mode makes the Research/Plan boundary explicit and welds the Context7 gate onto the research half. Run the research pass first (producing `{phase}-RESEARCH.md`), enforcing that any fact about *how an external technology actually behaves* is checked against current docs **before** it's written, then hand the grounded research to the planner for `{phase}-PLAN.md`.

**Why splitting is worth it**: `plan-phase` spawns `gsd-phase-researcher` → `RESEARCH.md`, then `gsd-planner` reads that file as settled input and builds the executable plan from it; `gsd-executor` later implements against the plan. **None of the downstream agents re-verify the research.** So a single stale assumption baked into `RESEARCH.md` doesn't just mislead one step — it silently shapes the whole plan and the code that follows. Research is the cheapest place to catch a wrong assumption before it compounds, and the highest-leverage gate in the flow.

### 0 — Args

Arg = the Phase number, optionally followed by `plan-phase` flags (`--tdd`, `--mvp`, `--gaps`, `--skip-verify`, `--text`, `--prd`, …). No Phase number → ask *"要为哪个 Phase 做计划？给我 Phase 编号。"* and wait. The user's flags belong to the **plan pass** (step 2) and must reach it unchanged.

**`--gaps` short-circuit**: `--gaps` means the user is closing verification gaps, not planning fresh. `plan-phase --gaps` reads `VERIFICATION.md` and skips research by design, so there's nothing for the research pass to ground. **Skip step 1 entirely** and go straight to step 2 with `--gaps` (do **not** add `--skip-research`; let gap mode run as-is).

### 1 — Research pass: a grounded `RESEARCH.md`

Hand control to `plan-phase` in **research-only mode** so it spawns `gsd-phase-researcher`, writes `{phase}-RESEARCH.md`, and exits before the planner. The researcher carries Context7 tools, so the gate fires *inside* the research; your job is to attach the discipline so grounding happens before any external-behavior claim is recorded. Triggers and method: `common.md` §D.

Invoke with the Phase number and this **verbatim** constraint block:

```
Skill("gsd:plan-phase", args: "--research-phase <phase-number> --research 【Context7 文档门禁】写 RESEARCH.md 时，凡是某个结论取决于外部技术的真实行为——库或 SDK 能力、API 限制/配额/契约、版本差异、框架配置（Spring Boot / MyBatis-Plus 含 mybatis-plus-join / Spring Security 或 Sa-Token，以本项目实际所用为准 / Spring Cloud Gateway）、数据库方言（MySQL vs openGauss，本项目双方言）、CLI 用法——必须先用 Context7 查证当前文档（resolve-library-id 选 /org/project，再 query-docs 传完整问题，而非单个关键词；MCP 不可用时调用 context7-mcp skill），把计划将要依赖的那个具体构造（真实方法签名 / 属性名 / 文档化的限制 / 方言函数是否存在）核对清楚，再把该结论写进 RESEARCH.md，并在结论旁注明文档确认了什么。纯内部结论（业务规则、命名、范围边界、不依赖外部 API 的时序）无需查 Context7，按常规调研即可。研究完成即退出，不要进入 planner。")
```

Keep the constraint text exactly as written. `--research-phase` forces research-only (exiting before the planner) and `--research` forces a fresh pass even if `RESEARCH.md` exists — so the grounding actually runs instead of reusing a possibly-stale file. Research structure and the `RESEARCH.md` template belong to the researcher; don't draft them yourself.

If the researcher surfaces a tech-shaped claim and you can see the grounding didn't happen, consult Context7 right then, before the plan pass consumes it — **don't let it pass**.

### 2 — Plan pass: build `PLAN.md` on the grounded research

Run the planner on top of the just-grounded `RESEARCH.md`. Pass `--skip-research` so `plan-phase` goes straight to the planner (and its verify loop) instead of re-researching, plus the flags from step 0:

```
Skill("gsd:plan-phase", args: "<phase-number> --skip-research <pass-through flags>")
```

The planner spawn, the `gsd-plan-checker` verify loop, iteration to pass, and the `PLAN.md` write all belong to `plan-phase`. Don't pre-empt it by drafting tasks yourself.

(A `--gaps` run skipped step 1 — here invoke `plan-phase <phase-number> --gaps <other flags>` **without** `--skip-research`, since gap mode handles research-skipping itself.)

### 3 — Close out

```
## gsx --plan-phase — Done
Phase {N}：研究 + 计划完成，已写入 {N}-RESEARCH.md、{N}-PLAN.md
Context7 核对：{一行 —— 哪些库/API/版本/方言/CLI 结论经文档确认；若研究中全是内部结论则写「本次研究均为内部结论，未涉及外部行为」}
下一步（建议先评审）：gsx --plan-review {N} —— 用外部 Codex CLI 做跨 AI 计划评审，独立挑出假设漏洞 / 缺失边界 / 排序问题，再决定是否执行
下一步（或直接执行）：见上方 plan-phase 的提示（通常是 /gsd:execute-phase {N}）
```

Recommend `--plan-review` ahead of execution: right after a plan is written, neither the planner nor you are sensitive to your own blind spots, and an independent external model reading it cold finds problems at the point where they're still cheap — before any code. Once the review produces `REVIEWS.md`, `gsx --replan-phase {N}` folds it back in, closing the plan → review → replan loop.

If the run bailed before `PLAN.md` was written (the verify loop didn't converge, or the user stopped after research), say so plainly and name what *did* land (`RESEARCH.md` only, or nothing).

---

## Guardrails (both modes)

- **Context7 is not optional when external behavior decides the answer.** A technology choice / library capability / API limit / dialect question gets grounded **before** it's locked into `CONTEXT.md` or written into `RESEARCH.md` — the researcher, planner and executor downstream won't re-ask, so a stale assumption here propagates silently. Skipping is valid only for purely-internal conclusions.
- **Ground the exact construct, not the topic.** Querying "MyBatis-Plus" in general isn't the gate; confirming the specific method / property / limit / dialect-function the plan will commit to is. That's where the lag bites.
- **Research first, then plan — don't collapse them.** The whole point is that the planner consumes *grounded* research. Run step 1 to completion before step 2. The two passes are deliberate: `--research-phase` exits before the planner, `--skip-research` starts at it.
- **Don't re-implement the GSD commands.** Gray-area analysis, the question loop, research structure, the planner, the `gsd-plan-checker` verify loop and every file template live in `/gsd:discuss-phase` and `/gsd:plan-phase`. This mode sequences the passes and adds the gate.
- **`--gaps` skips the research pass.** Gap closure reads `VERIFICATION.md` and has no fresh research to ground.
- **One Phase per run.** A different Phase means a fresh invocation.
