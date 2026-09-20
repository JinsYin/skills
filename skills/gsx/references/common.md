# gsx shared conventions

Parsing rules, format definitions and gates reused across modes. Read the section you need; don't read it all.

| § | Contents | Used by |
|---|----------|---------|
| A | Phase / Plan / Task number parsing | nearly every mode |
| B | Locating acceptance files, parsing Gaps | `--uat-newgap` `--uat-quickfix` `--uat-planfix` `--uat-autorun` |
| C | Write-back templates and the write-back commit | `--uat-newtest` `--uat-newgap` `--uat-quickfix` `--uat-planfix` |
| D | Context7 docs gate | `--debug` `--discuss-phase` `--plan-phase` `--uat-planfix` |

## A. Number parsing

Phase dirs are `.planning/phases/{NN}-{slug}/` with `NN` zero-padded to 2 digits; the files inside carry the number only, no slug (`{NN}-PLAN.md`, `{NN}-UAT.md`).

- **Phase number** — a `Phase`-prefixed or bare number (`4` / `04` / `Phase 4`) → zero-pad to `04`. A decimal inserted phase (`10.1`) stays as-is, unpadded.
- **Plan number `X.Y`** — Phase X's Yth Plan; scope = every target task in that Plan. Plan files may carry a letter suffix, so glob: `ls .planning/phases/04-*/04-04*-PLAN.md` (catches `04-04a-PLAN.md`).
- **Task number `X.Y.Z`** — Phase X / Plan Y / Zth `<task>`; scope = that task. A bare `Task 3` = the 3rd task in the active Plan.
- Case, the `Phase`/`Plan`/`Task` prefix, and whitespace are all ignored.

**When blank, infer in this order — never guess**:

1. the Phase already under discussion in this conversation (an executor that just returned a checkpoint gate message, or a `--plan-review` that just finished, is talking about it);
2. `.planning/STATE.md` `Last completed phase` (use `Active phase` when the user's tone points at "the one I'm on right now");
3. still not unique → `AskUserQuestion`.

No `.planning/` → not a GSD project; tell the user and stop. A glob matching 0 or several → list the candidates, ask, stop.

## B. Locating acceptance files and parsing Gaps

### B1 — Locate

```bash
ls .planning/phases/{NN}-*/{NN}-VERIFICATION.md \
   .planning/phases/{NN}-*/{NN}-UAT.md \
   .planning/phases/{NN}-*/{NN}-HUMAN-UAT.md 2>/dev/null
```

- Both `{NN}-UAT.md` and `{NN}-HUMAN-UAT.md` exist → prefer `HUMAN-UAT.md`; note in the report which was chosen and which was left untouched.
- 0 matches → "Phase {NN} has no acceptance output — run `/gsd:execute-phase {NN}` or `/gsd:verify-work {NN}` first." Stop. gsx does not generate these files.

### B2 — UAT file structure (`/gsd:verify-work` output)

frontmatter (`status`/`phase`/`started`/`updated`) · `## Current Test` (`number`/`name`/`expected`/`awaiting`) · `## Tests` (`### N. <title>` + `expected:` + `result:` + optional `note:`) · `## Summary` (`total`/`passed`/`issues`/`pending`/`partial`/`skipped`/`blocked`/`open_gaps`) · `## Gaps`.

`result` has exactly four native states: `pass` / `issue` / `skipped` / `blocked` (not-yet-run is `pending`). verify-work's continuation and `/gsd:plan-phase --gaps` both read this vocabulary, so **never invent `fail` / `skip`**.

### B3 — The two Gap formats

**A. Markdown heading** (Phases 03/04/10):

```
### GAP-1：编辑机构无 UI 入口（severity: major）
<optional body: current state, files, outstanding items…>
```

Identifier: `### GAP-N` or `### ~~GAP-N~~` (closed / struck through).

**B. YAML list** (verify-work native, Phases 02/08):

```yaml
- truth: "<expected behavior>"
  status: open          # or failed / resolved
  reason: "<User reported: …>"
  severity: major
  test: 3               # = Test 3 under ## Tests
  artifacts:
    - path: "<file>"
      issue: "<problem>"
  missing:
    - "<outstanding item>"
```

No `GAP-N` name; index by `test: N` ("Test {N}'s Gap").

**Choosing**: any Markdown entries → Markdown; only YAML entries → YAML; both present (rare) → Markdown, and note "mixed formats" in the report; `## Gaps` missing or empty → default Markdown, first is `GAP-1`.

**Next number**: grep `### GAP-{N}` and `### ~~GAP-{N}~~`, take max N, new = N+1. **Closed/struck-through ones still count; numbers only increase and are never reused**, so they stay monotonic in time order. YAML style has no explicit name — give the new entry a `# GAP-{N+1}` comment where N = the current item count (including resolved).

### B4 — VERIFICATION file (`gsd-verifier` output)

Check frontmatter `status` first:

- `gaps_found` → the primary source is the frontmatter `gaps:` YAML list (`truth` / `status: failed` / `reason` / `artifacts[].path`+`issue`). Extract each as a Gap with a stable id (`VERIFY-1`, `VERIFY-2`); `truth` is the title.
- `passed` (or no `gaps:`) → no VERIFICATION Gaps.

Then read the `### Gaps Summary` prose as a supplement (usually mirrors the frontmatter); if the frontmatter has no `gaps:` but the prose does, extract from the prose. "no gap" / "no gaps" → none.

### B5 — Already closed (skip)

- VERIFICATION: entry `status: passed`/`resolved`, or the whole file `status: passed`, or the Gap is gone from `gaps:`.
- UAT Markdown: title struck with `~~`, or carrying `→ **已修复**` / `已修复` / `resolved`.
- UAT YAML: `status: resolved`/`done`/`closed`.

Anything matching none of the above is pending.

### B6 — Merge

Merge the open Gaps from both sources into one pending list. Gaps clearly referring to the same issue (high overlap in `truth`/title/root cause/files) → merge into one, noting the source (VERIFICATION / UAT / both).

- Both Gap sections missing or empty → "Phase {NN}'s acceptance output has no Gap records." Stop.
- All Gaps already closed → "All Gaps in Phase {NN} are already closed." Stop.

## C. Write-back templates and the write-back commit

Write back only the target entry, dated today (`date +%Y-%m-%d`, never hardcoded). Follow Chinese Markdown conventions: a space between Chinese and numbers, Chinese punctuation, and no Jinja `{}` placeholders inside YAML values that contain Chinese.

### C1 — Mark a Gap fixed

**Markdown style** — strike the title with `~~`, keep `（severity: …）` outside the strike, append `→ **已修复**`, and insert one line below:

```
### ~~GAP-1：编辑机构无 UI 入口~~（severity: major）→ **已修复**
**修复：** {quick-task {quick_id} | plan {NN}-{xx}（gap-closure）}，commit {hash}（{YYYY-MM-DD}）。{one sentence}
```

**YAML style** — set the entry to `status: resolved` and add `fixed_by: "quick-task {quick_id}, commit {hash} ({YYYY-MM-DD})"`.

If `## Summary` has `open_gaps:`, decrease it by the number fixed (never below 0).

### C2 — Register a new Gap

**Markdown style** (omit whole blocks for missing fields — no empty lines, no "none" placeholders):

```
### GAP-{N}：{title}（severity: {severity}）
**现状：** {reason}
**关联 Test：** Test {test}{write「（无对应 Test）」when test is 0}
**涉及文件：**
- `{path}` —— {issue}
**待补：**
- {missing}
**备注：** {notes}
```

**YAML style** (omit the whole field when artifacts/missing/notes are empty — never write `artifacts: []`):

```yaml
- # GAP-{N}
  truth: "{title}"
  status: open
  reason: "{reason}"
  severity: {severity}
  test: {test}
  artifacts:
    - path: "{path}"
      issue: "{issue}"
  missing:
    - "{missing}"
  notes: "{notes}"
```

Judge `severity` from the **actual consequence**, don't ask the user: crash/exception/unavailable → `blocker`; wrong behavior or missing feature → `major`; deviates/intermittent/slow → `minor`; purely visual → `cosmetic` (manual registration may also use `trivial`).

### C3 — Register a new Test

```
### {N}. {title}
expected: {expected}
result: {result}
```

Multi-line variant (2-space indent, consistent with the file):

```
### {N}. {title}
expected: |
  {line 1}
  {line 2}
result: {result}
```

When `result != pending` and the user supplied evidence, append `note: {note}` (or a `note: |` block).

Single vs multi-line: contains newlines or exceeds 80 chars → force multi-line; otherwise follow the file's majority style (multi-line if >50% of existing entries use `expected: |`); `## Tests` empty → default single-line.

Test numbering: grep all `### N.`, take max integer N, new = N+1. **Every Test counts regardless of result; numbers only increase and are never reused.**

### C4 — frontmatter `updated:` and `## Summary`

- Set `updated:` to the current ISO-8601 UTC to the second (`date -u +"%Y-%m-%dT%H:%M:%SZ"`, never hardcoded). Field exists → edit it; frontmatter exists without it → insert below `started:`; no frontmatter → don't force one, note it in the report.
- `## Summary`: `total:` +1; the matching result count +1 (mind the name shifts: `pass`→`passed:`, `issue`→`issues:`); a missing field where `total:` exists → insert keeping the order `total / passed / issues / pending / partial / skipped / blocked / open_gaps`; preserve inline comments and append the reference (e.g. `pending: 2  # Test 4 待跑；Test 5（新增）`). `## Summary` entirely absent → don't force one, note it in the report.

### C5 — The write-back commit

An acceptance write-back is a standalone doc change (code and quick/plan docs were already committed by `/gsd:*`), so give it its own atomic commit:

```bash
git add .planning/phases/{NN}-*/{NN}-*UAT.md   # only paths actually edited this run
git commit -m "docs({NN}): {description}"
```

Scope `git add` to exact file paths — **never `git add -A` / `git add .`**. Concurrent GSD work may have other files staged; this skill commits nothing but its own acceptance write-back and must never sweep up code or someone else's changes. If nothing was written back, there is nothing to commit. Record the hash in the report.

## D. Context7 docs gate

**No flag, always on.** Cost is self-limiting: a purely internal conclusion never reaches a lookup, so no switch is needed.

**Why**: your training data lags real API / dialect / CLI behavior, and once such a conclusion lands in `CONTEXT.md` / `RESEARCH.md` / a fix plan, the planner and executor downstream treat it as settled and won't re-verify. Catching a stale assumption at the cheapest point — before it's written — beats discovering it at acceptance, by which time a full plan + execute cycle has burned.

**Triggers — whenever a conclusion turns on how an external thing actually behaves**:

- **Library / SDK capability** — whether an API exists, what it returns, a default, a documented limit, a real method signature.
- **API limit / quota / contract** — rate limits, payload caps, auth requirements, pagination rules of an upstream or third-party API.
- **Version differences** — behavior that differs across versions; a deprecation or breaking change.
- **Framework configuration** — Spring Boot / MyBatis-Plus (incl. mybatis-plus-join) / Spring Security or Sa-Token (whichever this project uses) / Spring Cloud Gateway property, annotation, auto-config, lifecycle.
- **Database dialect** — a function or syntax in MySQL but not openGauss (or vice-versa). This project ships both (Flyway double-path) and dialect mismatches are a recurring trap, so dialect-dependent conclusions always get grounded.
- **CLI / tool usage** — a command flag or subcommand the conclusion would rely on.

**Purely internal conclusions get no lookup** — own business rules, naming, scope boundaries, which fields to expose, sequencing that depends on no external API, a missing UI entry, wrong copy. Querying docs for those wastes a round-trip and dilutes what downstream actually needs. Judge by the **root cause**, not the wording; when the root cause is genuinely unclear but the `truth`/`reason` names a library, dialect or API, that's signal enough to ground it.

**How to consult** (per the global Context7 rule): `resolve-library-id` with the library name + what you're looking for → pick the best-matching `/org/project` → `query-docs` with the **full question**, not a single keyword. Tool names vary by environment (`mcp__context7__*` or `mcp__plugin_context7_context7__*`); use whichever is present. If the MCP is unreachable, degrade in order: ① invoke the `context7-mcp` skill; ② use `WebFetch`/`WebSearch` against the **official docs site** (not a random blog) — that is *degraded grounding*, not a skip, so say so and cite the URL.

**Ground the exact construct, not the topic.** Querying "MyBatis-Plus" in general isn't the gate; confirming *this* method's real signature, *this* property's real name, whether *this* dialect function exists — that is. The lag bites at exactly that layer.

**Enumerate every implicated technology, not just the loudest one.** A root cause usually names one external thing (openGauss rejecting `HOUR()`), but the fix edits code living inside *another* (a MyBatis-Plus `@Select` mapper). Before consulting, list the full set: **the technology named in the cause ∪ the framework/library/SDK owning the code you'll actually change**. That framework often offers a cleaner officially-supported way, or imposes a constraint that rules out your first idea. (Real example: MP's docs show the supported multi-dialect mechanism is XML `databaseId`, but this project is no-XML, so the real path is `@SelectProvider`, not the "dual `@Select`" you'd guess; and mybatis-plus-join's `selectFunc` only passes the function string through, giving no dialect portability. You learn both only by querying MP *and* MPJ.) Skipping the framework-of-the-edit is the most common way this gate half-fires.

**Consult in the main context, never via a subagent.** gsd subagents have been observed without the Context7 MCP tools actually exposed, which turns the gate into a fabricated "confirmation" — worse than no gate, because downstream then trusts it.

**Write what was confirmed explicitly into the conversation** (and pass it downstream as each mode requires): one line each — the construct checked, what the docs confirmed or refuted, the source `/org/project`. If the docs **refute** the assumed root cause (the fix everyone expected won't work), that's the single most valuable thing you can hand over — state it plainly rather than softening it. When you judge something purely internal and skip the lookup, say why, so the user sees a decision rather than an omission.
