---
name: self-improve
description: Retrospect an agent session (failures, user corrections, detours, repeated problems, token-heavy or slow turns and subagents), distill reusable lessons that make skills more correct, cheaper and shorter, and turn them into minimal, concise edits to the loaded skills from the jinsyin/skills repo — or a new skill — each shipped as a GitHub Issue plus linked PR via `gh`. A self-evolving feedback loop (RSI) for skills. Args `[--sessions] [--dry-run] [focus]`. Explicit invocation only — run when the user or another skill calls it; never auto-invoke.
---

# self-improve

Session evidence → lessons → minimal skill diffs → Issue + PR. The PR is the human review gate, so open it without asking for approval; a human merges.

Upstream: `jinsyin/skills` (skills live in `skills/<name>/`). Keep the main context lean: delegate transcript reading and each Issue/PR to a subagent when one is available, handing over only the lessons and paths.

Args: `--sessions` retrospect user-picked sessions of this project instead of only the current one; `--dry-run` stop after step 4 (plus step 6's findings) and print the report; free text narrows the focus.

## 1. Collect evidence

- Default: the current conversation plus `python3 <skill-dir>/scripts/transcript.py digest` (newest session of cwd). The digest is compact and is the only source of token and time data, so run it even when the context looks complete.
- `--sessions`: run `transcript.py list`, show the numbered list, let the user pick any N (numbers or id prefixes), then `transcript.py digest <id-prefix> ...`.

Record provenance for the Issue: source project name (git root basename), agent runtime, and for every retrospected session its id and name. On Claude Code, `transcript.py meta [<id-prefix> ...]` prints id, name, runtime, and the most-used and last `model/effort` pair; bare `meta` gives the current session, whose `last` pair is this improvement run's. On other runtimes, take them from your own environment; unknown → `unknown`.

The digest marks `USER*` (possible correction), `ERROR`, `REJECTED`, `[retry xN]`, `[repeat-error xN]`, `SKILL`/`SKILL-LOADED` (with path), and cost lines: `[cost]` totals for the main agent and subagents, `[heavy-turn N]` (a turn using ≥15% of input, with its skills, calls and wall time — wall time includes waiting on the user), `HEAVY-AGENT` (subagent ≥200k tokens), `BIG-RESULT` (tool output >20k chars). Markers are hints; judge each by context.

## 2. Scope

Candidate skills = skills used in the evidence (Skill call, slash command, `SKILL-LOADED`, or reading/editing the skill's own files) ∩ skills from upstream: entries in the project's `skills-lock.json` whose `source` is `jinsyin/skills` (case-insensitive), or a load path inside a `jinsyin/skills` checkout. Lessons that belong to no loaded skill can still justify a new skill. `self-improve` itself is always a candidate (see step 6). Everything else (third-party skills, the project's own code) is out of scope — mention it in the final summary only.

## 3. Extract lessons

Look for: user corrections, a rule/instruction/config that existed but did not take effect, wrong-phase mistakes, detours and abandoned approaches, retries, tool errors, questions the agent asked that a skill should have answered, repeated manual steps.

Also look for waste a skill caused, since cutting tokens and flow length is as much a goal as correctness: steps that add no value, steps that could merge or run in parallel, broad reads where a targeted grep would do, re-reading what is already in context, oversized or over-scoped subagents (or heavy inline work that a subagent should isolate), strong models on mechanical subtasks, and interview rounds the skill could have defaulted.

Gate each lesson:
- **Strong** (1 occurrence is enough): explicit user correction or rework caused by a skill gap or an ignored rule; a `heavy-turn`, `HEAVY-AGENT` or `BIG-RESULT` clearly caused by a skill instruction.
- **Weak** (needs ≥2 occurrences, across one or more sessions): detours, retries, tool errors, repeated questions.
- Below the gate → list in the summary, no Issue.

Keep only lessons that change *future* behavior beyond this one project. Drop one-off typos, project-specific facts, and model slips a rule would not have prevented.

## 4. Root-cause against latest upstream

Clone once into the scratchpad (or a temp dir): `gh repo clone jinsyin/skills <tmp>/skills -- --depth 1`. If cwd already is a `jinsyin/skills` checkout, `git fetch` and add a `git worktree` on `origin/<default-branch>` instead, leaving the user's working tree alone. Read the target skill there — not the possibly stale installed copy.

For each lesson decide:
- **Already covered upstream** → drop (installed copy is just stale; note it for sync). This includes corrections already fixed later in the same session, e.g. while authoring that skill.
- **Rule exists but did not fire** → fix *why*: wording, placement, precedence, discoverability. Never add a duplicate rule.
- **Gap** → add the smallest instruction to the owning section.
- **No owner and reusable across projects** → new skill (`skills/<name>/SKILL.md`, matching existing skills' style).

Minimal-diff rules: edit the smallest owning passage; prefer rewording over adding, and deleting or merging over rewording when a step is waste; write in the fewest words that still change behavior, since every word is paid for on every load; no restructuring; keep the skill's language and tone; growth per pass ≤ ~20% of the file. Explain *why* in the instruction itself rather than adding ALL-CAPS MUSTs.

Dedupe before writing: `gh issue list -R jinsyin/skills --state all --search "<skill> <keywords>"` and the same for `gh pr list`. An open match → add the new evidence as a comment on it and skip; a closed-as-rejected match → skip unless the evidence is materially new.

`--dry-run` ends here: print the report (step 5 structure) and stop.

## 5. Issue + PR, one pair per skill

Group all lessons for the same skill into one pair. In the clone:

1. Follow the repo's own contribution conventions (`CLAUDE.md`, `AGENTS.md`, commit style, `CHANGELOG.md` `[Unreleased]` entry in the file's language).
2. Issue: fill `.github/ISSUE_TEMPLATE/skill-improvement.md` (drop its front matter) and create it:
   `gh issue create -R jinsyin/skills --title "<type>(<skill>): <summary>" --label self-improve --label <skill> --body-file <file>`, one `--label` per improved skill (create missing labels first with `gh label create <name> -R jinsyin/skills`). The Issue is the report — provenance (step 1), evidence quotes, failing step, the rule that did not fire, proposed fix, and lessons below the gate.
3. Branch `self-improve/<skill>-<issue#>`, apply the diff, commit, push.
4. PR: fill `.github/pull_request_template.md`, `gh pr create -R jinsyin/skills --base <default-branch> --label self-improve --label <skill> --body-file <file>` with `Closes #<issue#>`.

Never push to the default branch and never merge.

## 6. Improve self-improve

Last, retrospect this run of `self-improve`: ambiguous or missing instructions you had to guess at, `transcript.py` errors or noisy output, wasted calls, and this run's own cost in the digest, and any correction the user made to this run. Apply the same gate, root-cause, and dedupe; ship survivors as their own `self-improve` Issue + PR (in `--dry-run`, add them to the report). Judge only this skill's instructions, not the lessons it produced.

## 7. Wrap up

Print a short table: skill · lesson · Issue · PR, plus skipped/below-gate items. Then ask whether to sync the changed skills into this project. On yes, copy the changed files from the PR branch over each installed copy (`.claude/skills/<name>`, `.agents/skills/<name>`, …; resolve symlinks and write to the real target once). Note that re-running `npx skills@latest add jinsyin/skills` after merge makes it official.
