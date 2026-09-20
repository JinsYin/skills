# `--uat-quickfix` / `--uat-planfix` — close acceptance Gaps

The first half is identical for both: locate and parse the Gaps (`common.md` §B) → show the scope and confirm. Then they fork:

- **`--uat-quickfix`** — fix Gaps one by one via `/gsd:quick`, one Gap per quick-task per commit. For **few, scattered, small** Gaps.
- **`--uat-planfix`** — batch via `/gsd:plan-phase --gaps` + `/gsd:execute-phase --gaps-only`. For **many, multi-file, needs planning**.

**Boundary**: orchestrate only (parse → fix → write back → commit the write-back). Code, PLAN.md and code commits come 100% from the invoked `/gsd:*` commands. The only files written here are the Gap source files (`*-VERIFICATION.md`, `*-UAT.md` / `*-HUMAN-UAT.md`), and only after a Gap is confirmed fixed with a commit. Never touch STATE.md, never commit **code**, never switch branches or cut checkpoints — the only commit is the Gap-status write-back, with `git add` scoped to exact paths. One Phase per run.

Gaps in a `{NN}-AUTOTEST.md` are out of scope — tell the user to fix those with `gsx --quick`.

## 0 — Parse args

Phase number per `common.md` §A. Additionally:

**`--uat-quickfix`** recognizes two more things:

- **`--discuss`**: strip it out first, from anywhere in the args, then record `DISCUSS=yes` **literally in the conversation** (Skill has no variable persistence, and step 4b runs once per Gap — it needs to read the decision back). Absent → `DISCUSS=no`. Everything else is parsed with the flag already removed, so `--discuss` can never be mistaken for a Phase or Gap token.
- **Gap name**: `GAP-1` / `VERIFY-1` / `gap 1` / `verify 1` / `GAP-01` / `gap-2` (ignoring case, hyphens, spaces) → `GAP-{n}` or `VERIFY-{n}`. A bare number with no `gap`/`verify` keyword is the Phase number. Gap name blank → fix **all open Gaps**.

`--discuss` is a **run-level** switch, not a per-Gap one: it applies to every Gap this run fixes. It changes nothing about how Gaps are selected, skipped or written back — its only effect is turning each `/gsd:quick` call in step 4b into `/gsd:quick --discuss`, giving that Gap a lightweight discussion phase before planning instead of the default fast path. Users reach for it when root causes are still fuzzy and a blind fast fix would likely miss. It's the only flag this wrapper knows; if the user writes some other `--flag`, don't guess — say it isn't recognized and ask whether they meant `--discuss`.

**`--uat-planfix`**'s Context7 gate (step 3.5) has no flag and always runs. If the user passes `--research` anyway, that's just them naming the default: accept it, strip it, and **never forward it** (reason at the end of step 3.5).

## 1–2 — Locate and parse the Gaps

Follow `common.md` §B1 (locate) → §B4 (VERIFICATION) → §B3 (the two UAT Gap formats) → §B5 (already closed) → §B6 (merge).

`/gsd:plan-phase --gaps` natively reads both VERIFICATION and UAT, so `--uat-planfix` does **not** feed UAT Gaps separately — it parses them only to show the scope and to know which entries to write back.

## 3 — Show the scope and confirm

List the pending Gaps (name / title / severity / source / linked Test).

**`--uat-quickfix`**: state alongside the table which pipeline is about to run — `/gsd:quick` (默认档) or `/gsd:quick --discuss` (讨论档). With >1 Gap selected, `AskUserQuestion` (header `Fix scope`): "准备用 `/gsd:quick{ --discuss}` 逐个修 N 个 Gap，每个自成一个 quick-task + commit{（discuss 档：每个 Gap 都会先讨论，耗时略长且会逐个交互提问）}。开始吗？" → `逐个开始修` · `只修其中几个（请指定）` · `取消`. The cost note is worth stating because the flag multiplies across Gaps — a user who typed `--discuss` for one stubborn Gap may not have pictured it running four times. It's a heads-up, not a veto: if they confirm, run all N with discussion. A single Gap goes straight to step 4.

**`--uat-planfix`**: `AskUserQuestion` (header `Fix scope`): "跑 `/gsd:plan-phase {NN} --gaps` 再 `/gsd:execute-phase {NN} --gaps-only`，覆盖 N 个 Gap？" — mention that Gaps with external-technology root causes get Context7-checked first, so the docs pass isn't a surprise. → `开始（计划 + 执行）` → step 3.5 · `只修其中几个（请指定）` (a narrowed scope also narrows step 3.5 — only ground the Gaps still in scope) · `取消`.

---

# `--uat-quickfix`: the fix half

## 4 — Fix each Gap via `/gsd:quick`

Process in order; finish one before starting the next.

### 4a — Suitability

Read all of this Gap's details (VERIFICATION: `truth`, `reason`, `artifacts`; UAT: `expected`, `root_cause`, `missing`), then:

- **Not a code defect** — "needs manual follow-up testing" / "depends on a data prerequisite, real SDK, or upstream API" / "needs manual user action (restart, reset DB)" / "external env or doc issue with no clear code change point" → **skip**; don't call `/gsd:quick`; record the skip reason.
- **Potentially large** — spans subsystems, needs research, multi-file features → still pass it to `/gsd:quick`, but warn: if `/gsd:quick` judges the scope too large and suggests `/gsd:plan-phase --gaps`, mark that Gap "not fixed (scope exceeds quick)".
- **Everything else** (a clear code / config / doc defect) → 4b.

### 4b — Invoke

```
Skill("gsd:quick", args="修复 Phase {NN} 验收 Gap「{Gap name or title}」（来源：{source file}）：{description / reason / root_cause}。期望行为：{truth / expected}。已知线索：{artifact paths / missing items / issue}")
```

With `DISCUSS=yes`, identical but with `--discuss` leading the args, so `/gsd:quick` parses it as a flag rather than as part of the Gap description. Every Gap in the run gets the same treatment — **don't decide per Gap**.

`/gsd:quick` runs its full flow (investigate → backend change needs plan confirmation → edit → commit → write `.planning/quick/{id}/` → update STATE.md); under `--discuss` it additionally discusses gray areas before planning, which takes longer and may ask questions per Gap — let it, and **don't answer on the user's behalf**. On return, record `quick_id` + commit hash, then:

- Fixed with a commit → step 7 to write this Gap back.
- User undid or cancelled, or no commit (no changes) → do **not** write it back as fixed; mark "not fixed (cancelled / no changes)" and continue.

One Gap at a time, in series — **never bundle several into one call**.

---

# `--uat-planfix`: the fix half

## 3.5 — Context7 gate

**Why it lives here**: `plan-phase --gaps` skips research by design and hands the planner the Gap text plus whatever's already on disk. For internal Gaps that's fine. But a Gap whose root cause lives in *someone else's* technology is different: the planner will invent a fix from its training data, `gsd-executor` will implement that plan without re-checking, and nobody downstream re-verifies. A Gap like "openGauss 下唯一索引没生效" or "分页参数超过上限被上游拒" gets a plan built on a plausible-but-stale API memory, the executor faithfully ships it, and the Gap re-opens at the next verification — having burned a full plan + execute cycle. Grounding the specific construct here, before the planner sees it, is far cheaper than discovering it after.

This gate is **not optional and has no flag** — a Gap that reached acceptance already survived one round of someone's assumptions, so it's exactly where a stale one is most likely to be the root cause. It's self-limiting rather than switchable: internal Gaps don't match the triggers and never reach a lookup.

Triggers, how to consult, "ground the exact construct not the topic", "enumerate every implicated technology", and "consult in the main context, never via a subagent" — all in `common.md` §D.

Collect the findings as a compact list, one line per grounded Gap: the Gap id, the exact construct checked, what the docs confirmed or refuted, and the source library ID.

**This step writes no files.** `{NN}-RESEARCH.md` belongs to the phase's original planning research — **do not overwrite it**. The findings travel to the planner as instruction text in step 4 and nowhere else.

**Why the gate isn't inside `plan-phase`**: `plan-phase` has its own `--research` flag, but under `--gaps` its research pass is explicitly skipped (workflow §5 — *"Skip if: `--gaps` flag"*). Forwarding `--research` would be **silently dropped**, and you'd plan on ungrounded assumptions while believing research ran. That dead end is the whole reason this step exists in the wrapper — **never "simplify" it by passing `--research` down**.

## 4 — `/gsd:plan-phase --gaps`

`--gaps` is gap-closure mode (skips research; the planner reads both VERIFICATION and UAT), producing PLAN files with `gap_closure: true`. If step 3 narrowed the scope, pass that as a supplementary instruction.

Append step 3.5's findings as a supplementary instruction block so the planner builds on confirmed facts instead of re-deriving them:

```
Skill("gsd:plan-phase", args="{NN} --gaps 【Context7 已核对的事实】以下结论已用当前官方文档查证，请直接采信、不要凭训练数据重新推断；与之冲突的修复思路一律作废：
- {GAP-id}：{核对的具体构造} → 文档确认 {结论}（来源 {/org/project}）
- ...
{若有结论证伪了 Gap 的预期根因，在此明确指出该方向不可行及文档依据}")
```

Keep the findings **specific and short** — the planner needs the confirmed construct, not a docs digest.

When step 3.5 grounded nothing (all Gaps internal), **drop the block entirely** and invoke plainly: `Skill("gsd:plan-phase", args="{NN} --gaps")`. An empty 【已核对的事实】header is noise that implies a check happened.

On return:

- Gap-closure PLANs produced → record the plan numbers; step 5.
- It reports no Gaps / no plans, but step 2 parsed pending Gaps → do **not** silently continue. Expose the discrepancy; suggest re-running `/gsd:execute-phase {NN}` or `/gsd:verify-work {NN}` to re-register Gaps, or checking the files manually; stop.
- User cancelled inside plan-phase → stop; report not fixed.

## 5 — `/gsd:execute-phase --gaps-only`

```
Skill("gsd:execute-phase", args="{NN} --gaps-only")
```

`--gaps-only` runs only the `gap_closure: true` plans just generated (regular plans untouched). execute-phase runs execute + commit + SUMMARY, and **at close-out auto re-runs `gsd-verifier`, regenerating `{NN}-VERIFICATION.md`**.

> ⚠️ On `--gaps-only` for the same Phase (not a decimal sub-phase), `close_parent_artifacts` (which auto-resolves UAT Gaps) does NOT trigger, but `verify_phase_goal` regenerates VERIFICATION.md from the latest code. So: the fresh VERIFICATION.md is authoritative; UAT.md is **not** auto-updated — which is why step 7's write-back is this mode's main value.

On return: normal completion with commits → step 6. Mid-execution failure / cancelled / no commits → write nothing back as fixed, record honestly, but still do step 6's mapping (most will land "not closed").

## 6 — Map results

Closure primarily trusts the fresh `{NN}-VERIFICATION.md`, cross-referenced with the plans plus SUMMARY/commit:

1. Re-read `{NN}-VERIFICATION.md`: the whole file `status: passed`, or a Gap gone from `gaps:` / flipped to passed → closed in the verifier's view.
2. Read each gap-closure PLAN (step 4) and its matching `{NN}-*-SUMMARY.md` (step 5). For each pending Gap, find the closure plan addressing it — match by id (`GAP-N`/`VERIFY-N`), `truth`/title, root cause, or files — and record the plan number + commit hash.
3. Judge:
   - Addressed by a closure plan executed with a commit, and the new VERIFICATION no longer reports it (or the Gap was UAT-only with no VERIFICATION counterpart) → **fixed**.
   - Not addressed, or its plan failed / produced no commit, or the new VERIFICATION still reports it → **not closed**; record the reason (not in plan / execution failed / cancelled / re-verify still failed).

**When uncertain, prefer "not closed + manual confirmation" over optimistically marking it fixed.**

---

# Write-back and reporting (both modes)

## 7 — Write back (fixed Gaps only)

For each Gap judged **fixed**, edit its source file per `common.md` §C1 — only that entry, dated today. `--uat-quickfix` writes `quick-task {quick_id}，commit {hash}`; `--uat-planfix` writes `plan {NN}-{xx}（gap-closure），commit {hash}`.

**VERIFICATION file**:

- `--uat-quickfix` — when the Gap came from or appears in `*-VERIFICATION.md`: in the frontmatter `gaps:` list set that entry `status: failed` → `resolved` (or `passed`) and add `fixed_by:`; in the `### Gaps Summary` prose append `→ **已修复**（quick-task {quick_id}, commit {hash}, {YYYY-MM-DD}）` after the matching description.
- `--uat-planfix` — the verifier already regenerated it, so **don't race it**. In order: ① the new VERIFICATION no longer reports this Gap (file `status: passed`, or the entry gone from `gaps:`) → already closed; no edit; note "VERIFICATION already re-verified and passed". ② It still has the entry but commit evidence proves it fixed (rare) → set that entry `failed`→`resolved`, add `fixed_by:`, and append `→ 已修复（plan {NN}-{xx}, commit {hash}, {YYYY-MM-DD}）` after the matching `### Gaps Summary` passage. If the prose can't be located precisely, don't force-edit; note it in the report.

If the UAT `## Summary` has `open_gaps:`, decrease it by the number fixed (never below 0).

Once every selected Gap has been written back, commit **once** per `common.md` §C5 — not per Gap:

```bash
git add .planning/phases/{NN}-*/{NN}-*UAT.md    # plus VERIFICATION.md ONLY if it was actually patched above
git commit -m "docs({NN}): 验收 Gap 修复回写（{fixed gap names}）"
```

For `--uat-planfix`, include VERIFICATION only in case ②; skip it in case ①. If nothing was written back (all skipped / cancelled / no changes), there is nothing to commit.

## 8 — Summary report

```
## gsx --uat-quickfix — Phase {NN}
Sources: {VERIFICATION filename (has/no Gaps)} + {UAT filename (has/no Gaps)}
Mode:    /gsd:quick{ --discuss}

Fixed:
- {Gap name}「{title}」（source: {VERIFICATION/UAT}）→ quick-task {quick_id}, commit {hash}

Skipped / not fixed:
- {Gap name}「{title}」—— {reason: 非代码缺陷 / 已取消 / 范围超出 quick…}

Write-back: {filename} marked {N} Gaps fixed. Committed as docs({NN}) {hash}.（一个都没修复则没有回写和提交。）
```

```
## gsx --uat-planfix — Phase {NN}
Sources:   {NN}-VERIFICATION.md（{has/no} Gaps）+ {UAT filename}（{has/no} Gaps）
Context7 核对：{one line per grounded Gap — 核对的构造 → 文档确认了什么（来源 /org/project）；若全部 Gap 均为内部问题则写「本次 Gap 均为内部问题，未涉及外部技术行为，无需查证」}
Planning:  /gsd:plan-phase {NN} --gaps → plans {list}
Execution: /gsd:execute-phase {NN} --gaps-only（VERIFICATION：{passed / gaps_found}）

Fixed:
- {Gap}「{title}」（source: {VERIFICATION/UAT}）→ plan {NN}-{xx}, commit {hash}
Not closed:
- {Gap}「{title}」—— {reason} + 下一步（重跑本模式 / gsx --quick / 人工 / 先重新登记 Gap）

Write-back: {UAT filename} marked {N} fixed; VERIFICATION.md {已自动复验 / 补丁了 M 条}. Committed as docs({NN}) {hash}.
```

Every skipped or not-fixed item gets a reason plus a next step (manual follow-up / switch to `--uat-planfix` / re-run this mode).

## Guardrails

- Code changes go 100% through the `/gsd:*` commands; this mode writes and commits only the acceptance source files, and only after a confirmed commit. Cancellations and no-change outcomes are **never** written back as fixed.
- Skip already-closed Gaps (`~~struck~~` / `status: resolved` / `status: passed`).
- `--uat-quickfix`: one Gap = one `/gsd:quick` call, in series. `--discuss` doesn't change that shape — still one Gap per call, each discussing first — and is **never** a reason to do extra investigation, research or verification *here*; the discussion round belongs to `/gsd:quick`.
- `--uat-planfix`: the Context7 gate is default and unswitchable, and **`--research` is never forwarded** to `plan-phase` (it's silently dropped under `--gaps`). Step 3.5 writes no files; leave `{NN}-RESEARCH.md` alone. The gate changes what the planner knows, not what this mode may touch — every other boundary holds.
- When unsure a Gap is a code defect, prefer skip-with-note over forcing it into `/gsd:quick`.
- Reply in Chinese.
