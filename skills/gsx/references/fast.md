# `--fast` — trivial change, multi-round iterate then squash

The lightest tier of the quick family. Closed loop: call `/gsd:fast` inline → ask whether to keep tweaking → if yes call it again → once satisfied, squash all commits into 1 and leave one row in STATE.md.

**Boundary vs `--quick` (escalate, don't cross)**:

- `--fast` (this): any **trivial** change, frontend or backend, via `/gsd:fast` **inline** (no subagents, no PLAN/SUMMARY, no `.planning/quick/{id}/` dir), multi-round with a final squash.
- `--quick`: a weighted single problem (research / planning / cross-file / API semantics), via `/gsd:quick --discuss`, leaving PLAN/SUMMARY — it **discusses, researches and verifies** the change instead of applying it blind.

**Boundary**: orchestrate only. All code changes go through `/gsd:fast` (no Edit/Write of source here). Three direct non-source ops are allowed: ① the final squash (`git reset --soft` + re-commit) or undo (`git reset --hard`); ② normalizing the STATE.md table to one row at close-out; ③ parking and restoring unrelated uncommitted changes via `git stash` (step 1.6). One trivial change per run; a different problem means a fresh invocation. No branch switching. Reply in Chinese.

**Parked-changes rule**: if step 1.6 ran `git stash push` (recorded `STASH=yes`), the **final action on every exit path** — squash close-out, undo, no-change abort — MUST be `git stash pop` to restore the user's unrelated changes. The no-overlap precondition guarantees a clean pop; on the off chance of a conflict, **stop and report the stash ref** (`git stash list`) for manual recovery — never `git clean` / `rm`.

## 0 — Get the problem description

Arg = the small change. If blank, ask: *"要快改点什么？（一句话能说清的琐碎改动）"*. **Record that sentence verbatim in the conversation** — it is the default squash subject, since `/gsd:fast` produces no SUMMARY.

## 1 — Baseline + dirty-tree snapshot

```bash
BASELINE=$(git rev-parse HEAD)
git status --short
```

**Write into the conversation** (Skill has no variable persistence): the baseline literal (e.g. *"baseline: 5957369"*) — squash and undo both return there — **and** the list of uncommitted file paths (`DIRTY_FILES`). The dirty-tree **decision is deferred to step 1.6**, because it depends on which files this change will touch (identified in step 1.5).

## 1.5 — Trivial-scope check + escalation (before the first `/gsd:fast`)

`/gsd:fast` is only for **trivial** work: one sentence, ≤3 file edits, ≤1 minute, no research, planning or new deps. Assess read-only (Read/Grep/Glob — no guessing). Three exits:

- **Not trivial** (>3 edits, cross-file, needs research / planning / new deps / new components / new routes / architecture) → **escalate to `--quick`**. Tell the user: *"超出 fast 档 —— 更适合 gsx --quick（/gsd:quick --discuss：讨论 + 研究 + 计划校验 + 验证，留 PLAN/SUMMARY）。要切吗？"*
- **Value-semantics trap** (looks trivial, belongs in the backend) → **escalate to `--quick`**. Anything changing "what the API returns, or how a return value renders as a label": field localization, status in Chinese, enum·code → readable label, amount·date formatting, masking. The correct fix is usually backend (VO/Service/DTO/dict), not a hardcoded Vue map. **Exception**: if read-only inspection confirms this project does that translation purely on the frontend (frontend dict / i18n / label-map), it's pure-frontend trivial and may stay. **When in doubt, escalate.**
- **Truly trivial** (typo or copy fix, config value, version number, one import or `.gitignore` line, a constant, frontend spacing·color·border-radius, or an already-frontend-owned label translation) → step 2. Frontend or backend both fine, as long as it's genuinely trivial and not one of the two cases above.

Nothing in this tier confirms a change with the user before it lands — that's what `--quick`'s `--discuss` round is for — so escalate anything dangerous or weighted.

**While assessing, also record the file(s) this change will edit (`TARGET_FILES`) in the conversation** — step 1.6 needs them to decide whether to prompt. For a trivial change the read-only pass usually pins this to 1–3 concrete paths; if you can't confidently name them, treat it as *uncertain* in step 1.6.

## 1.6 — Dirty-tree decision (overlap-aware)

`/gsd:fast` uses **`git add -A`** — it sweeps **every** uncommitted change into its commit. Decide by whether this change's files collide with the pre-existing uncommitted ones:

- **Clean tree** (`DIRTY_FILES` empty) → nothing to sweep; go to step 2.
- **Dirty, no overlap** (`TARGET_FILES ∩ DIRTY_FILES = ∅` **and** target files confidently known) → **don't ask**. Park the unrelated changes so the run commits only this change's files:
  ```bash
  git stash push -u -m "gsx-fast-preserve-${BASELINE}"
  ```
  **Record `STASH=yes` in the conversation** and `git stash pop` on every exit (see the parked-changes rule). Go to step 2.
- **Dirty with overlap, or target files uncertain** → this change can't be cleanly isolated. `AskUserQuestion` (header `Dirty tree`): *"待修改文件与未提交变更重叠（或无法确定改动范围）—— /gsd:fast 会用 git add -A 一并提交。先 stash/commit 再来？"* Options:
  1. `我先自己处理（stash/commit），稍后再来` → stop; restart later.
  2. `继续（已有改动会被一并提交）` → go to step 2.

## 2 — First call

```
Skill("gsd:fast", args=problem description)
```

`/gsd:fast` takes over inline: its own scope check (it may suggest `/gsd:quick`), inline edits, a `git add -A` atomic commit, and — if STATE.md exists — an appended fast line. Don't interfere. On return → step 3.

## 3 — Check this round's commits

There's no task_dir or slug to identify, so check commits:

```bash
git log "${BASELINE}..HEAD" --oneline
```

- **0 commits** → it likely judged the work not trivial / suggested `/gsd:quick`, or there was nothing to change. **If `STASH=yes`, `git stash pop` first.** Relay: *"/gsd:fast 没有产生 commit（多半超出琐碎范围）。HEAD 未变。要切到 gsx --quick 吗？"*, then stop (step 8's no-change exit).
- **≥1** → show the commit list (hash + subject), go to step 4.

## 4 — Interactive prompt

`AskUserQuestion`, header `Continue?`: *"本轮完成（N 个 commit）。满意吗？满意就 squash 收尾；想继续调就告诉我改什么；要全部丢弃选撤销。"* Options:

1. `满意 —— squash 收尾` → step 6.
2. `全部撤销 —— git reset --hard 回到起点` → step 7.
- "Other" with free-text feedback → step 5.

## 5 — Keep tweaking: another round (no resume)

`/gsd:fast` is **stateless inline** — there is no `resume`. Each follow-up tweak is a new trivial task stacking a commit on HEAD.

1. **Restate the feedback**: *"用户反馈：{原话}。再调一次 /gsd:fast 处理这个微调。"*
2. **Re-run the step 1.5 trivial check** on the follow-up — if it pushes over the line (research / cross-file / value semantics), offer escalation to `--quick`.
3. **Call again**: `Skill("gsd:fast", args=this round's tweak)`
4. **Return to step 3** — re-check `git log BASELINE..HEAD`, ask "Continue?" again.

No hard cap, but after every 3 rounds without convergence, prompt: *"已经 3 轮了 —— 反复多轮往往说明它并不琐碎。继续 / squash 当前状态 / 全部撤销 / 切到 gsx --quick？"*

## 6 — Squash close-out (satisfied path)

### 6a — Commit subject (no SUMMARY exists)

1. The step 0 task description, normalized to ≤80 chars.
2. Too vague → the first fast commit's subject (`git log BASELINE..HEAD --oneline | tail -1`).

Infer `type`: `fix` (default), `style` (visual/CSS), `chore` (config/version/deps/build), `docs`, `refactor` (rename/reorg).

### 6b — Final confirmation (ask once)

`AskUserQuestion`, header `Squash confirmation`: *"把 N 个 commit squash 成 1 个，标题：`{type}: {subject}`。可以吗？"* Options: 1. `可以，开始 squash` → 6c. 2. `我要改标题` (Other = the new subject) → use it and **execute the squash immediately without re-asking**.

### 6c — Execute the squash + normalize STATE.md

```bash
git reset --soft "${BASELINE}"

# Restore STATE.md to baseline: clears stale per-round fast rows (6d adds one clean row); || true if there was none at baseline.
git checkout "${BASELINE}" -- .planning/STATE.md 2>/dev/null || true

git add -A
git commit -m "{type}: {subject}

Squashed N fast-edits (gsx --fast):
- {commit1 hash} {commit1 subject}
- {commit2 hash} {commit2 subject}
- ..."
NEW_COMMIT=$(git rev-parse --short HEAD)
```

### 6d — Append one row to STATE.md (only if the table exists)

Only when `.planning/STATE.md` has the "Quick Tasks Completed" table (5 columns `| # | Description | Date | Commit | Directory |`). **Read** it, find the last data row, and **Edit** to insert after it (match that row's full text → replace with "row + newline + new row", for uniqueness):

```
| fast | {one line: the subject or a clearer summary} | {YYYY-MM-DD} | {NEW_COMMIT} | — |
```

- Date from `date +%Y-%m-%d`.
- `#` column is the literal `fast`; `Directory` column is `—`.
- If a "Last activity:" line follows the table, update its date to today.
- Commit this row separately, keeping the code commit's hash clean:
  ```bash
  git add .planning/STATE.md
  git commit -m "docs(state): log gsx --fast {short summary}"
  ```

No STATE.md or no such table → **silently skip**.

**Restore parked changes (if `STASH=yes`)**: as the final action, `git stash pop`. Go to step 8.

## 7 — Undo everything

### 7a — Second confirmation

List the `BASELINE..HEAD` commits, then `AskUserQuestion` header `Confirm undo`: *"git reset --hard 回到 {BASELINE 短哈希}，丢弃 N 个 commit。不可逆。确认？"* Options: 1. `确认撤销` → 7b. 2. `算了，继续调` → step 4.

### 7b — Execute the undo

```bash
git reset --hard "${BASELINE}"
```

This reverts all tracked changes after the baseline, including the STATE.md rows. `/gsd:fast` uses `git add -A` so it normally leaves no untracked files, but run `git status --short` anyway; if any remain, list them and **let the user decide** — this mode never runs `git clean` / `rm`.

**Restore parked changes (if `STASH=yes`)**: after the reset, `git stash pop`. Go to step 8.

## 8 — Final summary

**Satisfied (squash):**
```
## gsx --fast — Done
Change:       {problem}
Iterations:   first call + {N-1} tweaks
Commits:      {N} → squashed into 1
Final commit: {NEW_COMMIT} {type}: {subject}（git show {NEW_COMMIT}）
STATE.md:     added 1 fast row (if the table exists)
```

**Undo:**
```
## gsx --fast — Undone
Change: {problem}
Discarded {N} commits; HEAD restored to start: {BASELINE short}
```

**No-change exit:**
```
## gsx --fast — Aborted (no changes)
Change: {problem}
/gsd:fast produced no commit (likely exceeds trivial scope); HEAD unchanged: {BASELINE short}
（需要的话可以切到 gsx --quick。）
```
