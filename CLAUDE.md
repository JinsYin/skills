# Project Conventions

- MUST write skills in English.
- MUST keep instructions and rules in skills concise.

## Evals

- MUST ship `evals/evals.json` with every skill, following the `skill-creator` schema; put fixtures under `evals/files/`.
- MUST write eval `prompt`s in Chinese to mirror real users, and all other eval fields in English.
- MUST cover every branch and guardrail with at least one eval, each with checkable `expectations`.
- MUST target `expectations` at what the skill adds: assert behavior a model misses without the skill, observable in its output or transcript.
- MUST include at least one eval whose `prompt` triggers the skill in natural language, without the `/<skill>` command.
- MUST update evals in the same change that alters the skill's behavior.

## Skill Workflow

Create or edit a skill in this order, running every step through push without pausing for confirmation; finish each step before the next, and stop only where a step says to ask the user:

1. `/skill-creator`: draft or revise the skill. Done when the evals satisfy every rule under Evals.
2. `/skill-optimizer`: tune activation, salience, and context cost.
3. `/writing-for-agents`: polish wording for agent readers.
4. `/caveman-commit`: write a Chinese message, then `git commit`.
5. Push: `git fetch origin`, `git rebase origin/<branch>` to keep history linear, then plain `git push`. On rebase conflicts in `CHANGELOG.md`, keep both sides with local entries on top; ask the user about any other conflict. On a rejected push, fetch, rebase, and retry. Done when `HEAD` equals `origin/<branch>`.

Steps 2–3 run only on agent-loaded files (`SKILL.md`, `references/*.md`, `rules/*.md`) added or modified in this change, and are done when every finding is applied or rejected with a reason. `AGENTS.md` is generated: edit `rules/` and rebuild it.
