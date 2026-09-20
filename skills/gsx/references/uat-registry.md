# `--uat-newtest` / `--uat-newgap` — register one entry in the UAT file

Both modes share one pipeline: parse → locate → detect the existing format → fill missing fields → warn on duplicates → append → update counts → commit. They differ only in whether the entry lands under `## Tests` or `## Gaps`.

**Boundary**: touch only the UAT file (`*-UAT.md` / `*-HUMAN-UAT.md`) — never source, STATE.md, SUMMARY, or `.planning/quick/`; no execution, no diagnosis, no fixing. The only thing committed is that single UAT file, with `git add` scoped to its path (`common.md` §C5), so it can never sweep up source or someone else's staged changes. No branch switching. **One entry per run** by default; re-invoke for more (the sole exception is `--uat-newgap` step 0b).

To run tests use `--uat-autorun` / `--uat-phase`; to fix Gaps use `--uat-quickfix` / `--uat-planfix`.

## 0 — Parse args

The arg is free text: a description, a Phase number, both, or neither.

- **Phase number** — parse and infer per `common.md` §A.
- **Description** — the remaining text, raw material for step 3.

Description empty → `AskUserQuestion` for one sentence:
- `--uat-newtest` (header `Test description`): covering "what to test / what to expect".
- `--uat-newgap` (header `Gap description`): covering "expected / current state / impact".

### 0b — Should this split into several Gaps? (`--uat-newgap` only)

If the description shows signs of bundling independent problems (a numbered list `1) 2) 3)`; enumerated 一、二、三; or clauses joined by 另外 / 还有 / 以及 / 再者 that each point at a different module, file or symptom), **don't default to splitting and don't default to merging** — confirm via `AskUserQuestion` (header `Split?`):

- `合并成一条 Gap（同根因时推荐）` — treat the whole description as one Gap and continue with the single-Gap flow.
- `拆成 {N} 条独立 Gap` — first restate each sub-problem you identified in one sentence so the user can confirm the boundaries; once confirmed, run steps 2–7 once per sub-problem (own numbering, own field-fill pass, own write), then fold everything into **one shared commit** at step 7.

Skip this question when the signal is weak (single symptom, single file, single causal chain).

## 1 — Locate the UAT file

```bash
ls .planning/phases/{NN}-*/{NN}-*UAT.md
```

- 0 matches → stop: "Phase {NN} has no UAT.md / HUMAN-UAT.md; run `/gsd:verify-work {NN}` first." This mode won't generate the file.
- Both `{NN}-UAT.md` and `{NN}-HUMAN-UAT.md` → prefer `HUMAN-UAT.md`; note the choice in the report.

## 2 — Detect the existing format + next number

Read the target section and match the new entry to the existing style (structures in `common.md` §B2/§B3, Test template in §C3).

**`--uat-newtest`**:

- `## Tests` has `### N.` + `expected:` entries → follow that structure and its single/multi-line style.
- `## Tests` absent or empty → default structured single-line; the first is Test 1 (step 5 adds the heading if missing).
- **Free-form report style** (`### 2.1 起栈`-type headings, no `### N.`+`expected:`+`result:`, e.g. Phase 14) → **fall back**: do NOT force the template. Tell the user "这是自由报告体 UAT，请手工追加，或先迁移成结构化格式" and stop.

**`--uat-newgap`**: determine Markdown vs YAML style per `common.md` §B3 and continue the numbering by its rules.

## 3 — Smart-parse, then fill missing required fields in one pass

Extract from the description; mark unknowns "ask".

**`--uat-newtest`**:

| Field | Clues | Required? |
|-------|-------|-----------|
| `title` | one sentence: "what object + what action" | required (ask if missing) |
| `expected` | the observable acceptance point ("期望：", "should see") | required (ask if missing) |
| `result` | "通过", "已通过", "待跑", "发现问题" | defaults to **`pending`** |
| `note` | actual evidence; only meaningful when result != pending | optional |

Fixed `result` candidates: `pending（尚未跑）(Recommended)` / `pass` / `issue（发现问题）` / `skipped（无法判定）` / `blocked（环境或依赖不可用）`.

When asking for `expected`, push for **observable assertions** ("接口 X 返回 200 且 R.data 含 vcId", "/console/users 出现带 Y 列的分页表格") rather than "应该能用"; give a short example in the question.

**`--uat-newgap`**:

| Field | Clues | Required? |
|-------|-------|-----------|
| `title` / `truth` | one sentence: "expected behavior / what should happen" | required (ask if missing) |
| `reason` | current state / "User reported: …" / "Autotest: …" | required (fall back to `title`) |
| `severity` | `blocker/major/minor/trivial`, or 阻塞/严重/小问题 | required (ask if missing, default `major`) |
| `test` | `Test 5`, "关联 Test 5", or a quote of a Test's expected | required (ask; `0`/`-` for none) |
| `artifacts` | file-path tokens (`/`, `.tsx`/`.java`/`.sql`/`.md`), possibly several | optional |
| `missing` | "需要…" / "补充…" / "缺少…" / "TODO" | optional |
| `notes` | other supplementary info | optional |

Fixed `severity` candidates: `blocker（阻塞主流程）` / `major（功能性，有绕行方案）(Recommended)` / `minor（体验/边缘场景）` / `trivial（文案/视觉）`. Before asking for `test`, read `## Tests` and list the case titles to pick from ("1. 冷启动登录 / 2. 参保人列表 … / 0. 不关联").

**Ask once**: pack ALL missing required fields into a **single** `AskUserQuestion` (max 4 questions, required-priority order). Don't poll field by field; if everything is present, don't ask.

## 4 — Duplicate-registration warning

Before writing, compare the extracted `title` (and `truth` for Gaps) against existing entry titles. Significant overlap (≥3 effective word tokens against one entry) → `AskUserQuestion` (header `Duplicate registration`):

- `新条目 —— 继续 (Recommended)` → step 5.
- `作为 Test X / GAP-X 的补充` → do **not** create a new entry; append a `**补充（{YYYY-MM-DD}）：** …` line under that entry instead (for a Test, under `note:`, inserting `note:` if absent; for a Gap, as a paragraph). Then go to step 6 with **all counts unchanged**.
- `不登记` → stop.

## 5 — Write the new entry

`Edit`-append at the **end** of the target section (just before the next `## ` heading, or EOF), with one blank line before and after. If the section is missing, add the heading (`## Tests` after the frontmatter and before `## Summary`; `## Gaps` after `## Summary`).

Templates live in `common.md`: §C3 for a Test, §C2 for a Gap. Omit whole blocks for missing fields — no empty lines, no "none" placeholders.

## 6 — Update frontmatter `updated:` and `## Summary`

Per `common.md` §C4:

- `--uat-newtest` → `total:` +1 and the matching result count +1 (`pending`→`pending:`, `pass`→`passed:`, `issue`→`issues:`, `skipped`→`skipped:`, `blocked`→`blocked:`).
- `--uat-newgap` → `open_gaps:` +1; if the field doesn't exist, insert `open_gaps: 1` below `blocked:`.

The step-4 "supplement" branch leaves every count unchanged.

## 7 — Commit

Commit that one UAT file per `common.md` §C5:

```bash
git add .planning/phases/{NN}-*/{NN}-*UAT.md
git commit -m "docs({NN}): UAT 新增 Test {N}（{title}）"     # --uat-newtest
git commit -m "docs({NN}): UAT 新增 GAP-{N}（{title}）"      # --uat-newgap
```

The "supplement" branch commits too (a supplement line was still written), with the message `docs({NN}): UAT Test {X} 补充说明` / `docs({NN}): UAT GAP-{X} 补充说明`. Skip the commit only when step 4 chose "不登记" and nothing was written. The step-0b split branch puts all sub-Gaps in one commit: `docs({NN}): UAT 新增 GAP-{N}~GAP-{M}（{count} 项）`. Record the hash in the report.

## 8 — Summary report

```
## gsx --uat-newtest — Phase {NN}（{filename}）
New Test registered:
- Test {N}：{title} · expected：{summary} · result：{result} · note：{summary or（无）}
Updated: `## Tests` appended · frontmatter `updated:` → {ts} · `## Summary` `total:` {old}→{new}, `{field}:` {old}→{new}
Committed as docs({NN}) {hash}.
下一步：gsx --uat-autorun {NN}（自动跑）· gsx --uat-phase {NN}（人工跑）· gsx --uat-newgap {NN}（登记 Gap）
```

```
## gsx --uat-newgap — Phase {NN}（{filename}）
New Gap(s) registered:
- GAP-{N}：{title} · severity：{severity} · 关联 Test：{test} · files：{count} · outstanding：{count}
-（one line per sub-Gap if step 0b split was confirmed）
Updated: `## Gaps` appended · frontmatter `updated:` → {ts} · `## Summary` `open_gaps:` {old}→{new}
Committed as docs({NN}) {hash}.
下一步：gsx --uat-quickfix {NN} GAP-{N}（逐个修）· gsx --uat-planfix {NN}（批量修）
```

## Guardrails

- Numbers only increase and are never reused (closed/struck-through entries and any result still count): new = max(N)+1.
- **Follow the existing format, don't enforce one**: single stays single, multi stays multi, Markdown stays Markdown, YAML stays YAML; free-form report → fall back and stop.
- Warn on duplicates; leave the decision to the user.
- frontmatter or `## Summary` entirely absent → don't force one; note it in the report.
- Reply in Chinese.
