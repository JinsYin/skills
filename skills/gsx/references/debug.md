# `--debug` — diagnose → ground in docs → plan → interview → route

One loop taking a reported symptom from "something's broken" to a landed, verified fix, without guessing.

**Why it exists**: jumping straight to a fix is how you fix the *symptom* and miss the *cause*. And even with the right cause, a fix written from memory of how a library "probably" behaves is how you ship a second bug. So two disciplines are forced before any code moves: (1) a scientific root-cause diagnosis via `/gsd:debug --diagnose`, and (2) a Context7 check whenever the cause is about *how some external thing actually behaves* — your training data lags real API/dialect/CLI behavior, and a debug fix is exactly where that gap bites.

**Boundary — diagnosis never fixes.** `/gsd:debug --diagnose` is read-only investigation; it produces a Root Cause Report and stops. This mode then decides the fix *with* the user. The Quick-fix path is owned end-to-end by `/gsd:quick --discuss`; the Manual-fix path is the only place this mode edits source itself. Reply in Chinese.

## 0 — Get the symptom

Arg = the bug / error / symptom. If blank, ask: *"出什么问题了？把现象、报错、复现路径说一句，我先诊断根因再修。"*

Capture whatever the user gives — error text, HTTP status, stack trace, the page or endpoint, expected vs seen. The richer this is the better the diagnosis; **don't pad it with guesses**.

**Tier check (don't force-fit)**:

- The user already *knows* the root cause and just wants it changed (no investigation needed) → `--quick` / `--fast` fits better; say so and stop unless they still want a diagnosis.
- A sprawling multi-subsystem failure needing a real investigation campaign → `/gsd:debug` (full, multi-cycle, with fix) may fit better; offer it and let the user confirm.
- Otherwise — a concrete bug worth root-causing before touching — continue. This is the sweet spot.

## 1 — Diagnose the root cause

First check whether a diagnosed session already covers this symptom; re-running diagnosis on a known cause wastes a cycle:

```bash
ls .planning/debug/*.md 2>/dev/null | grep -v resolved
```

- A note whose `trigger:` / symptoms clearly match and whose `status:` is `diagnosed` → **reuse it**: read it, tell the user you're reusing it, skip to step 2.
- Otherwise run a fresh diagnosis:

```
Skill("gsd:debug", args="--diagnose " + symptom)
```

`/gsd:debug --diagnose` runs the scientific-method investigation in its own context and writes `.planning/debug/<slug>.md` (`mode: diagnose_only`, `status: diagnosed`) — a Root Cause Report with hypothesis, confirming evidence, falsification test and a `fix_rationale`. **It applies no fix.** Let it drive; don't interfere.

On return, read the report and pull out three concrete anchors: the **confirmed root cause**, the **evidence**, and the **affected code** (file:line, the offending call or config). The next two steps need them.

## 2 — Context7 grounding gate

Classify the root cause and follow `common.md` §D. If the cause is about external behavior (library/SDK behavior, version differences, framework configuration, DB dialect, CLI usage) you **must** consult before proposing anything — no exceptions, no "I'm pretty sure".

Pay particular attention to §D's "enumerate every implicated technology": the technology named in the cause ∪ **the framework owning the code you'll actually change**. Grounding only the former is the most common way this gate half-fires.

If the cause is purely internal (own business logic, a missing null check, an inverted conditional, a typo, local state), no external API is in question — skip Context7 and go to step 3, stating briefly why, so the user sees a decision rather than an omission.

**Write what Context7 confirmed — or why you skipped it — explicitly into the conversation.** This grounding is the distinctive value of the mode; make it visible.

## 3 — Produce the fix plan(s)

Turn the grounded root cause into **one or more concrete options**. Real bugs often have a quick targeted fix and a more-correct-but-broader one — surface both so the user can choose the altitude. For each give:

- **What changes** — the actual file(s) / function / config and the concrete change (name the replacement call, property, query rewrite — grounded by step 2, not hand-wavy).
- **Scope & risk** — how many files, whether it touches backend / DB / migration, blast radius, what could regress.
- **Trade-off** — why pick this over the other (e.g. *"局部替换 `HOUR()`→`EXTRACT(HOUR FROM …)` 最小改动，但只治这一处；抽象方言层根治但动 3 个 Mapper"*).

If there's genuinely only one sensible fix, say so and present the single plan — **don't manufacture fake alternatives**.

## 4 — Interview: which plan, which fix path

Ask **two questions** and wait for the answer before routing. The *content* is fixed; only the *mechanism* adapts to the harness — never assume `AskUserQuestion` exists.

**Print the plans first, then ask — regardless of mechanism.** Before posing question 1, write each candidate plan's *core content* (its **What changes / Scope & risk / Trade-off** from step 3) into the conversation, so the user decides on substance rather than a one-word picker label. A terse option label alone is not enough; the plan body must be visible right above the choice.

**How to ask**:

- **Interactive question tool available** (Claude Code's `AskUserQuestion`, or a Codex build where `request_user_input` really renders a picker) → print the plan bodies, then batch both questions into one round. Preferred where supported.
- **No interactive question tool** (typically Codex) → **do NOT call `AskUserQuestion` / `request_user_input`** — it won't reach the user, and you must not self-answer a prompt they never saw. Write both questions as a plain **numbered Markdown list**, label every option so they can answer compactly (e.g. *"1: 方案 B，2: Quick fix"*), then **stop and wait** for their text reply. Resume routing only after they answer.

**The two questions (identical either way)**:

1. **修复方案** — one entry per plan from step 3: its one-line essence plus scope/trade-off. With only one plan, still present it and ask for a confirm-or-adjust.
2. **修复方式** — exactly two options:
   - `Quick fix（gsx --quick）` — hand the chosen plan to `/gsd:quick --discuss` (讨论 + 研究 + 计划校验 + 执行 + 验证). Best when it touches backend/DB, or when you want the structured, atomic, reversible flow.
   - `Manual fix` — this mode applies the edits itself and verifies on the running instance. Best for a small, well-contained change you want done in place now.

Respect the answers. If the user picks a plan but wants to tweak it, fold that into the chosen plan before routing.

## 5 — Route the fix

### 5a — Quick fix

Compose the chosen, grounded plan into one clear task statement (carrying the root cause, the concrete change, the file:line anchors, any backend/DB touch, and what Context7 confirmed), then run it as the `--quick` mode does:

```
Skill("gsd:quick", args="--discuss " + composed fix task)
```

`/gsd:quick` now fully owns the run. **Do not interfere or re-plan.** Your diagnosis established *what's wrong and why*; its discussion round settles *how to change it*. Complementary, not redundant — hand the root cause over and let it drive. On return → step 6.

### 5b — Manual fix

The only place this mode edits source. Apply the chosen plan with Edit/Write, scoped tightly to the root cause; don't drift into unrelated cleanup.

Then **verify on the running instance — do not claim fixed from a clean compile alone.** This project runs `spring-boot:run` without devtools, so a recompile isn't picked up live; rebuild and restart the affected service, then reproduce the original symptom and confirm it's gone:

- Backend change → recompile, then restart the affected service via the project's process-compose socket (e.g. `process-compose process restart dap-admin -u <sock>`). If `dap-common` changed, that's the stale-jar trap: rebuild common and restart its consumers.
- Then re-trigger the exact failing path (the endpoint/page/command from the symptom) and confirm the 500 / error / wrong behavior is gone. Prefer a real request over a hand-built one.

Show the user the diff and the verification result. **If verification fails, say so plainly with the output — don't paper over it**; loop back to step 3 with what you learned.

## 6 — Close out

- **Mark the debug note resolved** — set `.planning/debug/<slug>.md` frontmatter `status:` to `resolved` and `updated:` to today, so it drops out of the active-session list. (Quick-fix path: after `/gsd:quick` lands its commit. Manual-fix path: after verification passes.)
- **Final summary**:

```
## gsx --debug — Done
根因：{one-line confirmed root cause}（见 .planning/debug/{slug}.md）
Context7：{what current docs confirmed, or「未涉及外部行为，已跳过」}
方案：{chosen plan, one line}
修复方式：{Quick fix —— 见上方 /gsd:quick 的 close-out / Manual fix —— {commit or diff}，已在运行实例验证：{the passing request/output}}
```

If the user bailed during the interview (chose neither path, or it turned out to be a known cause needing only `--quick`), say so plainly — no fix landed, nothing committed.

## Guardrails

- **Diagnose before fixing, always.** The value is root-cause-first; don't let a confident-looking symptom tempt you into skipping `/gsd:debug --diagnose`.
- **Context7 is not optional when external behavior is implicated.** Library / version / framework / dialect / CLI causes get grounded in current docs before the plan — your memory of an API is exactly what a debug fix can't rely on. Skipping is valid only for purely-internal causes, and you must say why.
- **Don't pre-empt the discussion round.** On the Quick-fix path, flag backend involvement in the hand-off but leave the concrete endpoint→Controller→VO plan and its confirmation to `/gsd:quick --discuss`.
- **Manual fix means verifying on the running instance.** A clean compile is not a fix here. Restart and reproduce, or it isn't done.
- **One bug per run.** A different symptom means a fresh invocation. No branch switching.
