# Project Conventions

- MUST write skills in English.
- MUST keep instructions and rules in skills concise.
- MUST ship `evals/evals.json` with every skill, following the `skill-creator` schema; put fixtures under `evals/files/`.
- MUST write eval `prompt`s in Chinese to mirror real users, and all other eval fields in English.
- MUST cover every branch and guardrail with at least one eval, each with checkable `expectations`.
- MUST update evals in the same change that alters the skill's behavior.

## Skill Workflow

Create or edit a skill in this order:

1. `/skill-creator` — draft or revise the skill and its evals.
2. `/skill-optimizer` — tune activation, salience, and context cost.
3. `/writing-for-agents` — polish wording for agent readers.
4. `/caveman-commit` — write a Chinese message, then `git commit`.

Steps 2–3 cover every agent-loaded file in the skill: `SKILL.md`, `references/*.md`, `rules/*.md`. Skip `README.md` (human-facing), `assets/` (output templates), and generated `AGENTS.md` (rebuild it instead).
