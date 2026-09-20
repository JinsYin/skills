---
name: gsx
description: "Unified front-door to the GSD workflow (.planning/ + /gsd:* commands), dispatching 20 modes by --flag: --fast/--quick/--debug for trivial edits, one scoped problem, and root-cause debugging; --discuss-phase/--plan-phase/--plan-review/--replan-phase for the discuss → research+plan → cross-AI review → fold-back convergence loop; --ui-spec for the UI design contract; --code-review to audit and auto-fix changed source; --uat-phase/--uat-autorun/--uat-newtest/--uat-newgap/--uat-quickfix/--uat-planfix to run UAT, register Tests/Gaps, and close Gaps; --vrf-autorun/--vrf-review/--vrf-approved to pre-run a checkpoint's verify steps, audit the round's changes, and release the gate; --add-todo/--add-backlog to capture work. Use this skill whenever the user mentions a Phase number, planning/discussion/research/plan review, UAT/acceptance/Gap/checkpoint/release/approved, or says 'just fix this quickly', 'why is this failing', 'review the code', 'spec the UI', 'add a todo', 'park this idea' — or names gsx, gsx-fast, gsx-uat-autorun and friends. Prefer it over calling /gsd:* directly: the Context7 docs gate, prototype-fidelity constraints, acceptance write-back and commit hygiene live here, and calling the command directly loses them."
argument-hint: "--<mode> [args for that mode]"
---

# gsx — GSD workflow front-door

Wraps `/gsd:*` commands, attaches this project's gates and close-out, then hands the work to GSD.

**Core boundary — orchestrate, don't overreach.** Code changes, the writing of PLAN/RESEARCH/CONTEXT/SUMMARY, and code commits come 100% from the wrapped `/gsd:*` command. gsx itself does three things: parse args, attach the gate, write back and commit acceptance docs (with `git add` scoped to exact paths). It never touches STATE.md, never commits code, never switches branches. One object per run (one Phase / one problem / one checkpoint) — a different one means a fresh invocation. **Reply in Chinese throughout, following Chinese Markdown conventions.**

Three exceptions, each stated in its own mode: `--fast` may run non-source git ops (squash / undo / stash); the `--uat-*` and `--vrf-review` modes may write acceptance docs; `--debug`'s Manual-fix path may edit source itself. Everything else hands off.

## Dispatch

The first `--flag` in `$ARGUMENTS` picks the mode; the rest are that mode's args.

- **No flag given** → pick the closest match from the table by intent, and say which one you picked in one line before acting (picking wrong means running the wrong pipeline).
- **Flag not in the table** → don't guess; list the candidates and let the user choose.
- Inference rules when an arg is blank: `references/common.md` §A.

| flag | what it does | read |
|------|--------------|------|
| `--fast` | Trivial change: multiple inline `/gsd:fast` rounds → squash into 1 commit | `references/fast.md` |
| `--quick` | One scoped problem, via `/gsd:quick --discuss` | below |
| `--debug` | Diagnose root cause → Context7 → fix plans → interview → route | `references/debug.md` |
| `--discuss-phase` | Phase discussion → `CONTEXT.md` (Context7 gate) | `references/plan.md` |
| `--plan-phase` | Research → plan, two explicit passes (gate on research) | `references/plan.md` |
| `--plan-review` | External Codex CLI reads `PLAN.md` cold → `REVIEWS.md` | below |
| `--replan-phase` | Fold `REVIEWS.md` feedback back into `PLAN.md` | below |
| `--code-review` | `/gsd:code-review {NN} --fix --all` on changed source | below |
| `--ui-spec` | `/gsd:ui-phase` + prototype-fidelity / UI-UX / frontend constraints | below |
| `--uat-phase` | Conversational UAT, `/gsd:verify-work` | below |
| `--uat-autorun` | Auto-run every case under `## Tests`, writing results back live | `references/autorun.md` |
| `--uat-newtest` | Append one Test to `## Tests` and commit | `references/uat-registry.md` |
| `--uat-newgap` | Append one Gap to `## Gaps` and commit | `references/uat-registry.md` |
| `--uat-quickfix` | Fix Gaps one by one via `/gsd:quick` → write back (few, scattered, small) | `references/uat-fix.md` |
| `--uat-planfix` | Batch Gaps via `plan-phase --gaps` + `execute --gaps-only` → write back (many, multi-file) | `references/uat-fix.md` |
| `--vrf-autorun` | Auto-run a `checkpoint:human-verify` task's `<how-to-verify>` steps | `references/autorun.md` |
| `--vrf-review` | Layer-by-layer change summary + frontend-patch overreach audit | `references/vrf.md` |
| `--vrf-approved` | Validate, then reply the `<resume-signal>` to release the gate | `references/vrf.md` |
| `--add-todo` | `/gsd:capture` — turn an aside into a structured todo | below |
| `--add-backlog` | `/gsd:capture --backlog` — park an idea as a 999.x entry | below |

**Typical chain**: `--discuss-phase` → `--plan-phase` → `--plan-review` → `--replan-phase` → `/gsd:execute-phase` → (at a checkpoint) `--vrf-autorun` → `--vrf-review` → `--vrf-approved` → `--uat-phase` / `--uat-autorun` → `--uat-quickfix` / `--uat-planfix` → `--code-review`.

## Codex adapter

In Codex, translate this wrapper instead of rewriting it:

- `$ARGUMENTS` = the text after `$gsx`.
- `Skill("gsd:<name>", args="…")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map it to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options or plans, print each option's core content in your reply, list the choices as a numbered Markdown list, then **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use the equivalent Codex tools.
- Preserve wrapper boundaries: if GSD owns the edit, don't make it here.
- Where a subagent is used (`--uat-autorun`'s execution layer), run those sections inline if you have no equivalent — the split saves tokens, it isn't a correctness requirement.

---

# Thin alias modes

These five groups are pure hand-offs; their whole body is here, so no reference file is needed.

## `--quick` — one scoped problem

`/gsd:quick` defaults to the fast path and skips discussion, which suits a task you already know cold. This mode exists for the opposite case: make `--discuss` the default so a fuzzy problem gets discussed — assumptions surfaced, gray areas clarified, decisions captured in `CONTEXT.md` — before planning, rather than blind-fixed. That discussion lives entirely inside `/gsd:quick`; there is nothing to add on top.

Arg = the problem description. If blank, ask: *"这次要做什么？先用一句话描述这个问题。"*

Two cases are worth redirecting rather than force-fitting, because the tier matters more than the entry point:

- **Genuinely trivial** (typo, one constant, spacing/color, a single config line) → `--fast` fits better; `--discuss` would spend a discussion round on a one-liner. Say so and stop unless the user still wants it here.
- **Large multi-subsystem feature** needing a roadmap → `/gsd:plan-phase` + `/gsd:execute-phase` fits better. Say so and let the user confirm.

Anything else — a real, scoped problem:

```
Skill("gsd:quick", args="--discuss " + problem description)
```

`--discuss` must lead, or it gets parsed as part of the description. `/gsd:quick` then owns the run: discuss, plan, execute, commit. Let it drive — including its questions, which are the point of `--discuss`. **Never answer them on the user's behalf.**

Close-out: `/gsd:quick` produces its own (quick_id / commit / task_dir). Don't re-summarize the code work it already reported; add one line of framing:

```
## gsx --quick — Done
问题：{problem}
交付：见上方 /gsd:quick 的 close-out（quick_id / commit / task_dir）。
```

If the user cancelled inside `/gsd:quick`, or it produced no commit, say plainly that nothing landed — this layer never touched the tree, so there's nothing to clean up.

## `--plan-review` — cross-AI plan review by Codex

Parse the Phase number (§A) → call `/gsd:review --phase {N} --codex` → relay and point at `--replan-phase`. The command owns everything: detecting the Codex CLI, building the review prompt from `PLAN.md`, invoking Codex, collecting the response, writing `REVIEWS.md`. **This layer never reviews the plan itself and never edits any file.**

**Why Codex specifically**: an independent external model reading the plan cold catches what the planner (and you, having just written it) are blind to — unstated assumptions, missing edge cases, a sequencing flaw, an over-scoped task. A cross-AI pass buys *divergent* judgment before the plan goes to execution, where mistakes get expensive. For a different or wider panel (`--gemini`, `--all`), call `/gsd:review` directly.

Prerequisite: the Phase must already have a `PLAN.md`. If not, send the user to `gsx --plan-phase {N}` and stop.

```
Skill("gsd:review", args="--phase {N} --codex")
```

If the Codex CLI isn't installed or detected, the command will say so — relay that plainly; **never** silently substitute another reviewer.

```
## gsx --plan-review — Phase {N}
Command:  /gsd:review --phase {N} --codex
Reviewer: Codex CLI
Report:   .planning/phases/{NN}-*/{NN}-REVIEWS.md
Verdict:  {one line — Codex's headline take}
Concerns: {count by severity, else a one-line gist}

下一步：gsx --replan-phase {N} —— 把本次评审意见（REVIEWS.md）回灌进计划，重新生成 PLAN.md
```

**Always give that next step** — `REVIEWS.md` exists to be consumed, and leaving it unread wastes the review. HIGH concerns → make the recommendation emphatic (a plan shouldn't reach execution with open HIGH concerns). Codex found nothing material → still mention `--replan-phase` is available but note it's optional; the user can go straight to `/gsd:execute-phase {N}`.

**Boundary**: this stops at `REVIEWS.md`. Folding feedback into `PLAN.md` is a separate deliberate step (`--replan-phase`) — kept apart so the user **reads the critique before the plan changes**. This is also not code review (that's `--code-review`, which audits implemented source).

## `--replan-phase` — fold review feedback into the plan

The third beat of the plan → review → replan loop. Parse the Phase number (§A) → call `/gsd:plan-phase {N} --reviews` → relay. `--reviews` makes plan-phase read the Phase's `REVIEWS.md` and re-run the planner so the regenerated `PLAN.md` answers the reviewers' concerns. The command owns the planner spawn, the `gsd-plan-checker` verify loop, and the `PLAN.md` rewrite; **this layer never drafts or edits the plan**.

Prerequisite: the Phase must already have a `REVIEWS.md`. If not, send the user to `gsx --plan-review {N}` first (or `gsx --plan-phase {N}` for a fresh plan) and stop. **Never run `--reviews` against a missing file.**

Trailing plan-phase flags (`--tdd` `--mvp` `--skip-verify` `--text` …) pass through unchanged.

```
Skill("gsd:plan-phase", args="{N} --reviews {pass-through flags}")
```

`--reviews` does not re-research, so the docs-grounded `RESEARCH.md` from `--plan-phase` stays intact — this is a plan revision, not fresh research.

```
## gsx --replan-phase — Phase {N}
Command:   /gsd:plan-phase {N} --reviews
Input:     .planning/phases/{NN}-*/{NN}-REVIEWS.md（Codex 评审意见）
Output:    .planning/phases/{NN}-*/{NN}-PLAN.md（已按评审意见重生成）
Addressed: {one line — which concerns were folded in / which were explicitly deferred}
下一步：/gsd:execute-phase {N}（若仍有未消化的意见，可再跑一轮 gsx --plan-review 复评）
```

If concerns remain unresolved, or the reviewer's points conflict with locked decisions, name that plainly rather than implying a clean sweep — the user may want another round or a manual call. If the verify loop didn't converge or the run bailed, say what state the plan is in (old `PLAN.md` untouched, or partially written).

## `--code-review` — audit changed source and auto-fix

Parse the Phase number (§A) → call `/gsd:code-review {NN} --fix --all` → relay. The command does all reviewing, fixing and `REVIEW.md` writing. **This layer never reads source looking for issues and never edits any source file or `REVIEW.md`.**

Flags are always appended together: `--fix` (spawn gsd-code-fixer, Critical+Warning by default) + `--all` (add Info to the fix scope). Pass through the user's `--depth=quick|standard|deep` / `--files=a,b` unchanged, with `--fix --all` last (`"{NN} --depth=deep --fix --all"`); add no other flags.

This audits the **changed code itself** (bugs/security/quality); `--uat-quickfix` / `--uat-planfix` close acceptance Gaps in `VERIFICATION.md` / `UAT.md`. Different jobs.

```
Skill("gsd:code-review", args="{NN} --fix --all")
```

The command runs its full flow (validate → config gate → file scoping → reviewer → `REVIEW.md` → fixer → summary). Don't interfere while it runs.

```
## gsx --code-review — Phase {NN}
Command:    /gsd:code-review {NN} --fix --all
Report:     .planning/phases/{NN}-*/{NN}-REVIEW.md
Findings:   Critical {n} · Warning {n} · Info {n}
Fixed:      {fixes applied (+ commits if any)}
Still open: {remaining / not auto-fixable / needs manual confirm}
```

Incomplete fixes or remaining findings → list the outstanding items plus next steps (manual / re-run / `gsx --quick`). No changed files or an empty scope → report that accurately, don't fabricate. Commits and branching belong to the command; if fixes sit uncommitted in the working tree, remind the user to confirm and commit.

## `--ui-spec` — generate the UI design contract

Arg = a single Phase number. If blank, ask *"要为哪个 Phase 生成 UI 设计契约？给我 Phase 编号。"* and wait.

Invoke with the number plus this **verbatim** constraint block:

```
Skill("gsd:ui-phase", args: "<phase-number> 必须逐屏引用 @.product/design/ 高保真（视觉+交互）原型（包括但不限于列表、卡片、弹窗、抽屉等视觉文案，以及产品交互），同时遵守 `ui-ux-best-practices` skill 的视觉与交互规范、`frontend-ui-best-practices` skill 的技术栈与结构基线（先读各自 SKILL.md 索引，再按需读取相关规则文件），以及 CLAUDE.md「本项目专属的 UI 约定」一节。如果页面中存在依赖后续 Phase 的功能，前端内容也必须先占位（比如用 disable、数字 0 占位）。如果有功能逻辑调整确需调整页面、不对齐原型的，必须采访我询问意见。最后如果前后端对接好了，前端必须清除相关页面的 mock 数据。")
```

Keep the constraint text exactly as written. Don't read the prototype or draft `UI-SPEC.md` yourself — hand off to `gsd:ui-phase`.

## `--uat-phase` / `--add-todo` / `--add-backlog` — straight through

Hand off immediately, no extra processing:

- `--uat-phase` — conversational UAT (questionnaire, manual verify guide, Gap recording, STATE.md updates):
  `Skill("gsd:verify-work", args=<remaining args>)`
- `--add-todo` — structured todo into `.planning/todos/pending/` (duplicate detection, area inference, STATE.md update, commit):
  `Skill("gsd:capture", args=<remaining args>)`
  Hand off even when the args are empty — capture will extract from recent conversation. **Don't** prepend `--note` / `--backlog` / `--seed` / `--list`; those route to different workflows.
- `--add-backlog` — add a 999.x parking-lot entry to `ROADMAP.md`, create the phase directory, commit:
  `Skill("gsd:capture", args="--backlog " + description)`
