# Project Conventions

## Core

- MUST write skills in English.
- MUST keep skill instructions/rules concise.

## Skill Evals

- MUST ship `evals/evals.json` with every skill, per `skill-creator` schema; fixtures under `evals/files/`.
- MUST write eval `prompt`s in Chinese (mirror real users); other eval fields English.
- MUST cover every branch and guardrail with ≥1 eval, each with checkable `expectations`.
- MUST target `expectations` at what skill adds: assert behavior model misses without skill, observable in output or transcript.
- MUST include ≥1 eval whose `prompt` triggers skill in natural language, no `/<skill>` command.
- MUST update evals in same change that alters skill behavior.

## Skill Workflow

Create/edit skill in this order, run every step through final sync without pausing for confirmation; finish each step before next; stop only where step says ask user:

1. `/skill-creator`: draft/revise skill. Done when evals satisfy every Skill Evals rule.
2. `/skill-optimizer`: tune activation, salience, context cost.
3. `/writing-for-agents`: polish wording for agent readers.
4. `/caveman-commit`: write Chinese message, then `git commit`.
5. Push: `git fetch origin`, `git rebase origin/<branch>` for linear history, then plain `git push`. Rebase conflicts in `CHANGELOG.md`: keep both sides, local entries on top; ask user on any other conflict. Push rejected: fetch, rebase, retry. Done when `HEAD` equals `origin/<branch>`.
6. Sync: refresh installed copies of added/changed skills, e.g. `npx skills@latest add jinsyin/skills --agent universal claude-code --skill foo bar`; if `setup-rules` changed, also run `/setup-rules update`. Commit in batches (skills, then rules) per step 4, push per step 5. Done when every sync change is committed and `HEAD` equals `origin/<branch>`.

Steps 2–3 run only on agent-loaded files (`SKILL.md`, `references/*.md`, `rules/*.md`) added/modified in this change; done when every finding applied or rejected with reason. `AGENTS.md` generated: edit `rules/`, rebuild.
