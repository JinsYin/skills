---
name: write-great-skill
description: "Workflow and eval bar for agent skills: draft with evals, polish, compress, verify, ship, with token-lean eval runs. Use whenever creating, editing or evaluating a skill (`SKILL.md`, `references/`, `rules/`, `evals/`), or when project conventions route root `CLAUDE.md`/`AGENTS.md` edits here, even if the user only says “改一下这个 skill” or “加个 eval”."
---
# write-great-skill

Workflow + quality bar for skills and agent-loaded docs. Project `CLAUDE.md`/`AGENTS.md` may add rules (eval prompt language, commit style, post-ship steps); project wins on conflict.

## Eval rules

- Ship `evals/evals.json` per `skill-creator` schema; fixtures under `evals/files/`, built by script (`init.sh`, `gen_fixtures.py`) once beyond a handful of files, so every run starts from identical state.
- Fixtures hold pre-task state only: header, comment or doc line spelling out behavior under test lets no-skill run copy it, so eval stops discriminating.
- Cover every branch and guardrail with ≥1 eval with checkable `expectations`.
- Aim `expectations` at what skill adds: behavior model misses without it, observable in output files or run's action log. Eval passing both ways stays only as regression guard, marked so in `benchmark.md`.
- ≥1 eval triggers skill in natural language, no `/<skill>` command.
- Update evals in same change that alters behavior.
- Record every run in `evals/benchmark.md` ([format](references/eval-runs.md#benchmarkmd)). Doubles as baseline cache: no-skill scores depend only on eval prompt, fixtures, model, never on skill text.

## Gates

| Trigger | Run |
|---|---|
| User asks | Step 1 → show draft, eval scores, open questions → ask user to confirm → steps 2–5 unattended |
| Another skill (e.g. `self-improve`) | Steps 1–5 unattended; project post-merge steps (e.g. sync) not run, named in PR |
| Only root `CLAUDE.md`/`AGENTS.md` changes | Edit → show diff → ask user to confirm → steps 2, 3, 5 unattended; no evals |

Unattended: stop only where a step says ask user.

## Steps

Steps 2–4 cover only agent-loaded files (`SKILL.md`, `references/*.md`, `rules/*.md`, root `CLAUDE.md`/`AGENTS.md`) added or modified in this change. Skill `AGENTS.md` generated from `rules/`: edit `rules/`, rebuild.

Only steps 1 and 4 run evals. Every subagent this skill dispatches (eval executor, grader, Ship) runs `model: sonnet`, `effort: high`: reliable on multi-step written instructions at fraction of session model's cost.

1. **Draft** — `/skill-creator`, running evals per [Eval runs](#eval-runs) instead of its own run loop, which reruns every eval and baseline each iteration; skip its HTML viewer and description optimization loop unless user asks (each costs more than it adds here). Done when evals satisfy Eval rules and scores in `benchmark.md`.
2. **Polish** — `/writing-for-agents`, inline. Done when every finding applied or rejected with reason.
3. **Compress** — `/caveman-compress` rules applied by hand to added/changed text only; untouched lines stay. Done when headings, code, URLs, paths unchanged.
4. **Verify** — `/skill-optimizer` checks (activation, salience, regressions) statically; rerun with-skill only, on evals covering text changed since their last run, against cached baselines. Done when every finding applied or rejected with reason and no eval regresses.
5. **Ship** — commit + push per project conventions, delegated to fresh subagent with handoff (changed paths, convention file, branch, project ship/sync steps, trigger row): inline, every git call resends whole authoring context. Done when it reports `HEAD` equals remote branch; relay its summary.

Named skill unavailable → apply its intent inline, note in final report.

## Eval runs

Two costs dominate: main context resent on every tool call, and eval executions. Keep both small:

- **Execute evals in subagents.** One fresh subagent per eval × config, all dispatched in one turn. Sonnet following skill = conservative check for stronger models.
- **Baselines once.** Dispatch no-skill runs only for evals new or changed in this change, or whose `benchmark.md` row used another model; reuse rest. Editing existing skill → regression baseline is its last with-skill row, not fresh old-skill run.
- **Scope reruns.** While iterating, rerun only evals covering edited branches, plus failures; full with-skill suite once before gate. One run per config; repeat single eval only to confirm suspected flake.
- **Executors get prompt and fixture only**, so skill gets tested, not leaked `expectations`. Prompt templates: [references/eval-runs.md](references/eval-runs.md).
- **Grade outside main context.** Script-checkable expectations → script; rest → one grader subagent per batch. Main agent reads only its score table and failing evidence.
