---
name: write-great-skill
description: "Workflow and quality bar for agent skills: draft, polish, compress, verify, ship. Use whenever creating or editing a skill (`SKILL.md`, `references/`, `rules/`), or when project conventions route root `CLAUDE.md`/`AGENTS.md` edits here, even if the user only says “改一下这个 skill”."
---
# write-great-skill

Workflow + quality bar for skills and agent-loaded docs. Project `CLAUDE.md`/`AGENTS.md` may add rules (commit style, post-ship steps); project wins on conflict.

No evals: never create `evals/`, run test prompts, baselines or benchmarks.

## Gates

| Trigger | Run |
|---|---|
| User asks | Step 1 → show draft, open questions → ask user to confirm → steps 2–5 unattended |
| Another skill (e.g. `self-improve`) | Steps 1–5 unattended; project post-merge steps (e.g. sync) not run, named in PR |
| Only root `CLAUDE.md`/`AGENTS.md` changes | Edit → show diff → ask user to confirm → steps 2, 3, 5 unattended |

Unattended: stop only where a step says ask user.

## Steps

Steps 2–4 cover only agent-loaded files (`SKILL.md`, `references/*.md`, `rules/*.md`, root `CLAUDE.md`/`AGENTS.md`) added or modified in this change. Skill `AGENTS.md` generated from `rules/`: edit `rules/`, rebuild.

1. **Draft** — `/skill-creator` for structure and writing only; skip its evals, HTML viewer and description optimization loop. Done when draft covers every branch and guardrail the user asked for.
2. **Polish** — `/writing-for-agents`, inline. Done when every finding applied or rejected with reason.
3. **Compress** — `/caveman-compress` rules applied by hand to added/changed text only; untouched lines stay. Done when headings, code, URLs, paths unchanged.
4. **Verify** — `/skill-optimizer` checks (activation, salience, regressions) statically. Done when every finding applied or rejected with reason.
5. **Ship** — commit + push per project conventions, delegated to fresh subagent (`model: sonnet`, `effort: high`) with handoff (changed paths, convention file, branch, project ship/sync steps, trigger row): inline, every git call resends whole authoring context. Done when it reports `HEAD` equals remote branch; relay its summary.

Named skill unavailable → apply its intent inline, note in final report.
