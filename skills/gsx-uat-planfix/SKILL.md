---
name: gsx-uat-planfix
description: "Docs-grounded batch-fix of a GSD Phase's acceptance Gaps via /gsd:plan-phase N --gaps then /gsd:execute-phase N --gaps-only, with a MANDATORY Context7 gate that always runs before planning — every Gap whose root cause turns on external technology behavior (library/SDK capability, API limit, version difference, framework configuration, DB dialect, CLI usage) is checked against current docs and the confirmed facts are fed to the gap planner, so the fix plan is never built on a stale assumption about how the tech actually behaves. Gaps come from both *-VERIFICATION.md (auto-verify; frontmatter status: gaps_found + gaps: list / ### Gaps Summary) and *-UAT.md / *-HUMAN-UAT.md ## Gaps (verify-work); plan-phase --gaps natively reads both, execute-phase --gaps-only runs only those plans, then write closed Gaps back as fixed. Arg is the Phase number (inferred from context / STATE.md if blank). Invoke when the user says 'fix Gaps with plan', 'batch-fix Phase X's Gaps', 'fix VERIFICATION/UAT gaps', 'research the gaps then plan the fix', 'gsx-uat-planfix'. vs gsx-uat-quickfix: that fixes Gaps one by one via /gsd:quick (few, scattered); this batches via plan-phase + execute-phase (many, multi-file, needs planning)."
argument-hint: "[optional: Phase number, e.g. 4 / 04 / Phase 4; inferred from context or STATE.md if blank]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Skill
  - AskUserQuestion
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
---

# gsx-uat-planfix

## Codex Adapter

In Codex, translate this Claude wrapper instead of rewriting it:

- `$ARGUMENTS` = text after `$gsx-*`.
- `/gsd:<name> ...` or `Skill("gsd:<name>", args="...")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options/plans, first print each option's core content in your reply, then list the choices as a numbered Markdown list and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.
- Preserve wrapper boundaries; if GSD owns edits, do not edit source here.


Batch-fix a GSD Phase's acceptance Gaps via "plan + execute". Two Gap sources, both parsed in step 2:

- **`*-VERIFICATION.md`** — `gsd-verifier` output from `/gsd:execute-phase N` close-out; Gaps when frontmatter `status: gaps_found`.
- **`*-UAT.md` / `*-HUMAN-UAT.md`** — `/gsd:verify-work N` output; Gaps in `## Gaps`.

`/gsd:plan-phase --gaps` natively reads both, so this skill does NOT feed UAT Gaps separately — it parses Gaps only to show scope and know which entries to write back.

**Boundary:** orchestrate only (parse → optional Context7 research → `/gsd:plan-phase --gaps` → `/gsd:execute-phase --gaps-only` → map → write back → commit the write-back). Code, PLAN.md, code commits come 100% from the two GSD commands. This skill writes only the Gap source files, and only after a Gap is confirmed fixed by a gap-closure plan + commit. Never touch STATE.md, commit **code**, switch branches, or release checkpoints — the only thing this skill commits is its own Gap-status write-back, scoped to the source file(s) it edited. One Phase per run. Reply in Chinese.

## 0 — Parse Phase number

Phase dirs: `.planning/phases/{NN}-{slug}/`, `NN` zero-padded to 2 digits.

- `$ARGUMENTS` has a number → normalize (ignore case, `Phase` prefix, spaces): `4`/`04`/`Phase 4` → `04`.
- Blank → infer: (1) Phase under discussion in conversation; (2) else `.planning/STATE.md` `Last completed phase`; (3) still ambiguous → `AskUserQuestion`, don't guess.
- No `.planning/` → not a GSD project; tell user and stop.

The Context7 gate (step 3.5) has no flag — it always runs. If the user passes `--research` anyway, that's just them naming the default; accept it, strip it, and don't forward it (see step 3.5's pass-through warning).

## 1 — Locate Gap source files

File names prefixed with number only (no slug):

```bash
ls .planning/phases/{NN}-*/{NN}-VERIFICATION.md \
   .planning/phases/{NN}-*/{NN}-UAT.md \
   .planning/phases/{NN}-*/{NN}-HUMAN-UAT.md 2>/dev/null
```

Parse both source types (Gaps may be in only one). If both UAT and HUMAN-UAT match, prefer `HUMAN-UAT.md`; note the choice in report.

- 0 files → "Phase {NN} has no acceptance output — run `/gsd:execute-phase {NN}` or `/gsd:verify-work {NN}` first." Stop.
- ≥1 match → continue.

## 2 — Parse and merge pending Gaps

### 2a — VERIFICATION file

Check frontmatter `status` first:

- `status: gaps_found` → primary source is the frontmatter `gaps:` YAML list (each entry: `truth` / `status: failed` / `reason` / `artifacts[].path`+`issue`). Extract each as a Gap with a stable id (`VERIFY-1`, `VERIFY-2`); `truth` = title, keep `status`/`reason`/`artifacts`.
- `status: passed` (or no `gaps:`) → no VERIFICATION Gaps.

Then check `### Gaps Summary` prose as supplement (usually mirrors frontmatter). If frontmatter has no `gaps:` but prose exists, extract from prose. "no gap"/"no gaps" → none.

### 2b — UAT file `## Gaps`

Two formats, both handled:

**A. Markdown heading** (Phases 03/04): `### GAP-1：编辑机构无 UI 入口（severity: major）` + optional body. Gap name = `GAP-{n}`; extract title, `severity`, body.

**B. YAML list** (verify-work native):
```yaml
- truth: "<expected>"
  status: failed       # or resolved
  reason: "<User reported: ...>"
  severity: major
  test: 3              # = Test 3 in ## Tests
```
No `GAP-N`; index by `test: N` ("Test {N}'s Gap").

### 2c — "Already closed" (skip)

- VERIFICATION: entry `status: passed`/`resolved`, or whole file `status: passed`, or Gap gone from `gaps:`.
- UAT Markdown: title struck `~~`, or has `→ **已修复**` / `已修复` / `resolved`.
- UAT YAML: `status: resolved`/`done`/`closed`.

Not matching any of the above = pending fix.

### 2d — Merge

Merge open Gaps from both sources into one pending-fix list. Gaps clearly referring to the same issue (high overlap in `truth`/title/root cause/files) → merge into one, noting source (VERIFICATION / UAT / both).

- Both Gap sections absent/empty → "Phase {NN}'s acceptance output has no Gap records." Stop.
- All Gaps already closed → "All Gaps in Phase {NN} are already closed." Stop.

## 3 — Show scope and confirm

Show pending-fix list (Gap name / title / severity / source / Test). `AskUserQuestion` (header `Fix scope`): "Run `/gsd:plan-phase {NN} --gaps` then `/gsd:execute-phase {NN} --gaps-only` covering N Gaps?" — mention that Gaps with external-technology root causes get Context7-checked first, so the docs pass isn't a surprise.

- `Start (plan + execute)` → step 3.5.
- `Fix only certain Gaps (specify)` → note scope, pass as supplementary instruction to plan-phase in step 4. A narrowed scope also narrows step 3.5 — only research the Gaps still in scope.
- `Cancel` → stop.

## 3.5 — Context7 gate

**Why it exists:** `plan-phase --gaps` skips research by design and hands the planner the Gap text plus whatever's already on disk. For internal Gaps that's fine. But a Gap whose root cause lives in *someone else's* technology is different: the planner will invent a fix from its training data, `gsd-executor` will implement that plan without re-checking, and nobody downstream re-verifies. A Gap like "openGauss 下唯一索引没生效" or "分页参数超过上限被上游拒" gets a plan built on a plausible-but-stale API memory, the executor faithfully ships it, and the Gap re-opens at the next verification — having burned a full plan + execute cycle. Grounding the specific construct here, before the planner sees it, is far cheaper than discovering it after.

This gate is **not optional and has no flag** — a Gap that reached acceptance already survived one round of someone's assumptions, so it's exactly the place where a stale assumption is most likely to be the root cause. The gate is self-limiting rather than switchable: it costs nothing on internal Gaps because they don't match the triggers below and never reach a lookup.

**Research each pending Gap only when its root cause turns on external technology behavior:**

- **Library / SDK capability** — whether an API exists, what it returns, a default, a documented limit, a method signature.
- **API limit / quota / contract** — rate limits, payload caps, auth requirements, pagination rules of an upstream or third-party API.
- **Version differences** — behavior that differs across versions; a deprecation or breaking change.
- **Framework configuration** — Spring Boot / MyBatis-Plus (incl. mybatis-plus-join) / Spring Security or Sa-Token (whichever this project uses) / Spring Cloud Gateway property, annotation, auto-config, lifecycle.
- **Database dialect** — a function/syntax in MySQL but not openGauss (or vice-versa). This project ships **both** dialects (Flyway double-path), so dialect-dependent Gaps always get grounded — dialect mismatches are a recurring trap here.
- **CLI / tool usage** — a command flag or subcommand the fix would rely on.

**Purely internal Gaps get no Context7 call** — missing UI entry, wrong copy, a business rule, a naming or scope-boundary miss. Querying docs for those wastes a round-trip and dilutes the findings the planner actually needs. Judge by the Gap's *root cause*, not its wording; when a Gap's root cause is genuinely unclear, a `truth`/`reason` that names a library, dialect, or API is enough signal to ground it.

**How to consult** (per the global Context7 rule): `mcp__context7__resolve-library-id` with the library/framework name + the question → pick the best-matching `/org/project` ID → `mcp__context7__query-docs` with the *full* question, not a single keyword. If the MCP tools aren't reachable, invoke the `context7-mcp` skill. Ground the **exact** construct the fix will commit to — the real method signature, the actual property name, the documented limit, whether the dialect function exists — not the topic in general. "Ask Context7 about MyBatis-Plus" isn't the gate; confirming *this* method's actual signature is.

Do this research **in the main context, right here** — do not delegate it to a subagent. The gsd subagents have been observed not to have the Context7 MCP tools actually exposed, which turns the gate into a fabricated confirmation. You have the tools in this context; use them.

Collect the findings as a compact list — one line per grounded Gap: the Gap id, the exact construct checked, what the docs confirmed (or refuted), and the library ID it came from. If the docs **refute** the Gap's assumed root cause (the fix everyone expected won't work), that's the single most valuable thing you can hand the planner — state it plainly rather than softening it.

This step writes **no files**. `{NN}-RESEARCH.md` belongs to the phase's original planning research — do not overwrite it. The findings travel to the planner as instruction text in step 4 and nowhere else.

**Why this gate lives here instead of inside `plan-phase`:** `plan-phase` has its own `--research` flag, but under `--gaps` its research pass is explicitly skipped (workflow §5 — *"Skip if: `--gaps` flag"*). So forwarding `--research` to it would be silently dropped and you'd plan on ungrounded assumptions while believing research ran. That dead end is the whole reason this step exists in the wrapper — never "simplify" it by passing `--research` down to `plan-phase`.

## 4 — /gsd:plan-phase --gaps

`--gaps` = gap-closure mode (skips research; planner reads both VERIFICATION + UAT). Produces PLAN files with `gap_closure: true`. If step 3 limited scope, pass that as supplementary instruction.

Append step 3.5's findings to the args as a supplementary instruction block, so the planner builds on confirmed facts instead of re-deriving them:

```
Skill("gsd:plan-phase", args="{NN} --gaps 【Context7 已核对的事实】以下结论已用当前官方文档查证，请直接采信、不要凭训练数据重新推断；与之冲突的修复思路一律作废：
- {GAP-id}：{核对的具体构造} → 文档确认 {结论}（来源 {/org/project}）
- ...
{若有结论证伪了 Gap 的预期根因，在此明确指出该方向不可行及文档依据}")
```

Keep the findings **specific and short** — the planner needs the confirmed construct, not a docs digest.

When step 3.5 grounded nothing (all Gaps internal), drop the block entirely and invoke plainly — an empty 【已核对的事实】header is noise that implies a check happened:

```
Skill("gsd:plan-phase", args="{NN} --gaps")
```

On return:
- Gap-closure PLANs produced → record plan numbers; step 5.
- No Gaps found / no plans, but step 2 parsed pending Gaps → do NOT silently continue. Expose the discrepancy; suggest re-running `/gsd:execute-phase {NN}` or `/gsd:verify-work {NN}` to re-register Gaps, or checking files manually; stop.
- User cancelled inside plan-phase → stop; report not fixed.

## 5 — /gsd:execute-phase --gaps-only

```
Skill("gsd:execute-phase", args="{NN} --gaps-only")
```

`--gaps-only` runs only the `gap_closure: true` plans just generated (regular plans untouched). execute-phase runs execute + commit + SUMMARY, and **at close-out auto re-runs `gsd-verifier`, regenerating `{NN}-VERIFICATION.md`**.

> ⚠️ On `--gaps-only` for the same Phase (not a decimal sub-phase), `close_parent_artifacts` (auto-resolves UAT Gaps) does NOT trigger, but `verify_phase_goal` regenerates VERIFICATION.md from latest code. So: fresh VERIFICATION.md is authoritative; UAT.md is NOT auto-updated — hence step 7 write-back is this skill's main value.

On return:
- Normal completion, commits produced → step 6.
- Mid-execution failure / cancelled / no commits → write nothing back as fixed; record honestly; still do step 6 mapping (most land "not fixed").

## 6 — Map results

Closure primarily trusts the fresh `{NN}-VERIFICATION.md`, cross-referenced with plans + SUMMARY/commit:

1. Re-read `{NN}-VERIFICATION.md`: whole file `status: passed`, or a Gap gone from `gaps:` / flipped to passed → closed in verifier's view.
2. Read each gap-closure PLAN (step 4) + matching `{NN}-*-SUMMARY.md` (step 5). For each pending Gap, find the closure plan addressing it: match by ids (`GAP-N`/`VERIFY-N`), `truth`/title, root cause, or files; record plan number + commit hash.
3. Judge:
   - Addressed by a closure plan executed with a commit + new VERIFICATION no longer reports it (or Gap was UAT-only with no VERIFICATION counterpart) → **fixed**.
   - Not addressed, or its plan failed/no commit, or new VERIFICATION still reports it → **not closed**; record reason (not in plan / execution failed / cancelled / re-verify still failed).

When uncertain, prefer **not closed + manual confirmation** over optimistically marking fixed.

## 7 — Write back (fixed Gaps only)

For each Gap judged **fixed**, `Edit` its source file — only that one entry, today's date.

### 7a — UAT file (primary target — not auto-updated by execute-phase)

**Markdown style** — strike title `~~`, keep `（severity: …）` outside, append `→ **已修复**`, note below:
```
### ~~GAP-1：编辑机构无 UI 入口~~（severity: major）→ **已修复**
**修复：** plan {NN}-{xx}（gap-closure），commit {hash}（{YYYY-MM-DD}）。{one sentence}
```

**YAML style** — set entry `status: resolved`, add `fixed_by: "plan {NN}-{xx} (gap-closure), commit {hash} ({YYYY-MM-DD})"`.

If UAT `## Summary` has `open_gaps:`, decrease by the number fixed (not below 0).

### 7b — VERIFICATION file (defensive)

Already regenerated by the verifier — don't race it. In order:
1. New VERIFICATION no longer reports this Gap (file `status: passed`, or Gap gone from `gaps:`) → already closed; no edit; note "VERIFICATION already re-verified and passed."
2. New VERIFICATION still has the entry but commit evidence proves fixed (rare) → set that `gaps:` entry `status` `failed`→`resolved`, add `fixed_by: "plan {NN}-{xx}, commit {hash} ({YYYY-MM-DD})"`; append `→ 已修复（plan {NN}-{xx}, commit {hash}, {YYYY-MM-DD}）` after the matching `### Gaps Summary` passage. If prose can't be located precisely, don't force-edit; note in report.

After all fixed Gaps are written back, commit the write-back. execute-phase already committed the code, plans, and the refreshed VERIFICATION.md; the Gap-status write-back belongs to no plan, so give it one atomic commit of its own:

```bash
git add .planning/phases/{NN}-*/{NN}-*UAT.md   # + {NN}-VERIFICATION.md ONLY if 7b case 2 actually patched it
git commit -m "docs({NN}): UAT Gap 修复回写（{fixed gap names}）"
```

Scope `git add` to the exact file path(s) this skill edited — the UAT file, plus the VERIFICATION file only when step 7b case 2 truly patched it (skip it when 7b found it already re-verified, case 1). Never `git add -A` / `git add .`: execute-phase and concurrent GSD may have other staged files, and this skill must commit **nothing** but its own acceptance write-back. Commit once at the end. If no Gap was written back (all not-closed), there is nothing to commit — skip it. Record the commit hash in the report.

## 8 — Summary report

```
## gsx-uat-planfix — Phase {NN}
Sources: {NN}-VERIFICATION.md ({has/no} Gaps) + {UAT filename} ({has/no} Gaps)
Context7 核对：{每个查证过的 Gap 一行 — 核对的构造 → 文档确认了什么（来源 /org/project）；若全部 Gap 均为内部问题则写「本次 Gap 均为内部问题，未涉及外部技术行为，无需查证」}
Planning: /gsd:plan-phase {NN} --gaps → plans {list}
Execution: /gsd:execute-phase {NN} --gaps-only (VERIFICATION: {passed / gaps_found})

Fixed:
- {Gap} "{title}" (source: {VERIFICATION/UAT}) → plan {NN}-{xx}, commit {hash}
Not closed:
- {Gap} "{title}" — {reason} + next step (re-run this skill / `/gsd:quick` / manual / re-register Gaps first)

Write-back: {UAT filename} marked {N} fixed; VERIFICATION.md {already refreshed / patched M entries}. Committed as docs({NN}) {write-back commit hash}. (If nothing was fixed, no write-back / commit was made.)
```

---

## Guardrails

- **The Context7 gate is default and unswitchable.** It has no flag: a Gap that reached acceptance already survived one round of assumptions, so it's the likeliest place for a stale one to be the root cause. Cost control comes from the trigger list (internal Gaps never reach a lookup), not from an opt-out. Same idiom as `gsx-plan-phase` / `gsx-debug`.
- **Never forward `--research` to `plan-phase`.** Under `--gaps` its research pass is skipped outright (workflow §5), so a forwarded flag is silently dropped and the grounding never happens. The gate fires only because step 3.5 runs it here.
- **Ground the exact construct, not the topic.** Confirm the specific method / property / limit / dialect-function the fix will commit to. Topic-level lookups don't catch the stale assumption that reopens the Gap.
- **Research in the main context, never via a subagent.** gsd subagents have been seen without the Context7 MCP tools actually exposed, which produces confident but fabricated "confirmations" — worse than no gate, because the planner then trusts them.
- **Only external-behavior Gaps get grounded.** Internal Gaps (UI entry, copy, business rules, scope) proceed straight to planning. Over-querying dilutes the findings the planner needs.
- **Step 3.5 writes no files.** `{NN}-RESEARCH.md` is the phase's original planning research — leave it alone. Findings reach the planner as instruction text only.
- **The gate changes what the planner knows, not what this skill may touch.** Every other boundary holds: no code, no STATE.md, no branches, no checkpoints — the only commit is the Gap-status write-back.
