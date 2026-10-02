---
name: self-improve
description: Retrospect agent sessions (failures, user corrections, detours, token-heavy or slow turns) into lessons, shipped as minimal edits to jinsyin/skills skills — or a new skill, or a `setup-rules` convention for a heavy manually-invoked third-party skill — each as GitHub Issue + PR. Args `[--sessions] [--dry-run] [focus]`. Invoke only when the user, a rule, or another skill calls for it.
---

# self-improve

Session evidence → lessons → minimal skill diffs → Issue + PR. PR = human review gate: open Issue + PR without asking approval; push only to `self-improve/*` branches, human merges.

Upstream: `jinsyin/skills` (skills in `skills/<name>/`). Keep main context lean: work from digest, open raw transcript only for specific turns. Subagents only for many `--sessions`; inline is cheaper otherwise.

Args: `--sessions` retrospect user-picked sessions of this project, not just current; `--dry-run` report only, no Issue/PR; free text narrows focus.

## 1. Collect evidence

- Default: current conversation + `python3 <skill-dir>/scripts/transcript.py digest` (newest session of cwd). Digest compact, only source of token/time data — run even if context looks complete.
- `--sessions`: run `transcript.py list`, show numbered list, user picks any N (numbers or id prefixes), then `transcript.py digest <id-prefix> ...`.

Record provenance for Issue: source project name (git root basename), agent runtime, each retrospected session's id + name. On Claude Code, `transcript.py meta [<id-prefix> ...]` prints id, name, runtime, most-used and last `model/effort` pair; bare `meta` = current session, its `last` pair = this improvement run's. Other runtimes: take from own environment; unknown → `unknown`. Done when digest read and provenance recorded for every session.

Digest marks `USER*` (possible correction), `ERROR`, `REJECTED`, `[retry xN]`, `[repeat-error xN]`, `SKILL`/`SKILL-LOADED` (with path), cost lines: `[cost]` totals for main agent + subagents, `[heavy-turn N]` (turn ≥15% of input) / `[skill-run N]` (other skill turn): one run's in/out tokens, calls, compactions, peak-ctx, subagents, result chars, wall time (includes waiting on user), skills; `HEAVY-AGENT` (subagent ≥200k tokens), `BIG-RESULT` (tool output >20k chars), `[skill-cost]`/`HEAVY-SKILL` (per-skill totals incl. its subagents; heavy = ≥25% of session tokens or wall time; `via=manual` = user-typed slash command, `auto` = Skill call by model or another skill). Markers = hints; judge each by context.

## 2. Scope

Candidate skills = skills used in evidence (Skill call, slash command, `SKILL-LOADED`, or reading/editing skill's own files) ∩ upstream skills: entries in project's `skills-lock.json` with `source` `jinsyin/skills` (case-insensitive), or load path inside a `jinsyin/skills` checkout. Lessons owned by no loaded skill can still justify new skill. `self-improve` always candidate (step 6). Third-party skills out of scope, except one tagged `HEAVY-SKILL via=manual`: retrospect its call details for lessons belonging in a `setup-rules` convention, since its files can't change here. Everything else (other third-party skills, project's own code) → final summary only.

## 3. Extract lessons

Look for: user corrections, rule/instruction/config that existed but didn't take effect, wrong-phase mistakes, detours + abandoned approaches, retries, tool errors, agent questions a skill should have answered, repeated manual steps.

Also waste a skill caused — cutting tokens and flow length is goal equal to correctness: no-value steps, steps that could merge or run parallel, broad reads where targeted grep would do, re-reading what's in context, oversized/over-scoped subagents (or heavy inline work a subagent should isolate), strong models on mechanical subtasks, interview rounds skill could have defaulted.

Gate each lesson:
- **Strong** (1 occurrence enough): explicit user correction or rework from skill gap or ignored rule; `heavy-turn`, `HEAVY-AGENT` or `BIG-RESULT` clearly caused by skill instruction.
- **Weak** (needs ≥2 occurrences, across one or more sessions): detours, retries, tool errors, repeated questions.
- Below gate → summary only.

Done when every lesson is Strong, Weak with ≥2 occurrences, or below gate.

Keep only lessons changing *future* behavior beyond this one project. Drop one-off typos, project-specific facts, model slips a rule wouldn't have prevented.

## 4. Root-cause against latest upstream

Clone once into scratchpad (or temp dir): `gh repo clone jinsyin/skills <tmp>/skills -- --depth 1`. If cwd already `jinsyin/skills` checkout, `git fetch` + add `git worktree` on `origin/<default-branch>` instead; leave user's working tree alone. Read target skill there — not possibly stale installed copy. Get `<default-branch>` via `gh repo view jinsyin/skills --json defaultBranchRef -q .defaultBranchRef.name`; never guess `main`.

Give every lesson exactly one verdict:
- **Already covered upstream** → drop (installed copy stale; note for sync). Includes corrections already fixed later same session, e.g. while authoring that skill.
- **Rule exists but did not fire** → fix *why* in that rule: wording, placement, precedence, discoverability; one rule stays single source of truth.
- **Gap** → add smallest instruction to owning section.
- **Heavy third-party skill** → rule steering how agent drives it (skip/override step, default answer, delegate, cap output), never copy of its content. Target `skills/setup-rules/assets/conventions/<ecosystem>.md` when one matches (e.g. `superpowers.md`); else create it + register in `setup-rules/SKILL.md` (convention order, file list, Workflow 2 menu).
- **No owner, reusable across projects** → new skill (`skills/<name>/SKILL.md`, matching existing skills' style).

Minimal-diff rules: edit smallest owning passage; prefer rewording over adding, deleting/merging over rewording when step is waste; fewest words that still change behavior — every word paid on every load; no restructuring; keep skill's language + tone; growth per pass ≤ ~20% of file. State target behavior positively and explain *why* in instruction itself; plain reasons steer better than ALL-CAPS MUSTs.

Dedupe before writing: `gh issue list -R jinsyin/skills --state all --search "<skill> <keywords>"`, same for `gh pr list`. Open match → add new evidence as comment, skip; closed-as-rejected match → skip unless evidence materially new.

`--dry-run`: skip step 5, run step 6, then print each would-be Issue body in full (filled template, step 5 language) so preview matches what would be filed.

## 5. Issue + PR, one pair per skill

Group all lessons for same skill into one pair; heavy third-party lessons join `setup-rules` pair, one extra `--label` per third-party skill. In step 4 clone/worktree:

1. Follow repo's contribution conventions (`CLAUDE.md`, `AGENTS.md`, commit style, `CHANGELOG.md` `[Unreleased]` entry in file's language).
   Issue + PR bodies: prose you author (field values, table cells, root cause, proposed change, change notes) in Chinese for the human reviewer; template skeleton verbatim in English so Issues read alike — headings, field keys (`Skill:`, `Source project:` …), table header, checklist items, `<model>/<effort>` pairs, Signal `strong`/`weak`. Session quotes verbatim.
2. Issue: fill `.github/ISSUE_TEMPLATE/skill-improvement.md` (drop front matter), create:
   `gh issue create -R jinsyin/skills --title "<type>(<skill>): <summary>" --label self-improve --label <skill> --body-file <file>`, one `--label` per improved skill (create missing labels first with `gh label create <name> -R jinsyin/skills`). Issue = report — provenance (step 1), evidence quotes, failing step, rule that didn't fire, proposed fix, lessons below gate. Cost lessons: one evidence row per cited run with its `[heavy-turn]`/`[skill-run]` fields, so reviewers compare runs without transcripts.
3. Branch `self-improve/<skill>-<issue#>`, apply diff, commit, `git push -u origin <branch>` unpiped so network failures surface; retry until pushed.
4. PR: fill `.github/pull_request_template.md`, `gh pr create -R jinsyin/skills --base <default-branch> --head <branch> --label self-improve --label <skill> --body-file <file>` with `Closes #<issue#>`.

## 6. Improve self-improve

Last, retrospect this `self-improve` run: ambiguous/missing instructions you guessed at, `transcript.py` errors or noisy output, wasted calls, this run's own cost in digest, any user correction to this run. Same gate, root-cause, dedupe; ship survivors as own `self-improve` Issue + PR (`--dry-run`: add to report). Judge only this skill's instructions, not lessons it produced.

## 7. Wrap up

Print short table: skill · lesson · Issue · PR, plus skipped/below-gate items. Then ask whether to sync changed skills into this project. On yes, copy changed files from local PR branch (shallow clone has no `origin/<branch>` refs) over each installed copy (`.claude/skills/<name>`, `.agents/skills/<name>`, …; resolve symlinks, write real target once). Note re-running `npx skills@latest add jinsyin/skills` after merge makes it official. If convention changed, tell user run `setup-rules update` to refresh `CLAUDE.local.md` (explicit-invocation only).