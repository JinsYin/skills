# Project Conventions

## Core

- MUST write skills in English.
- MUST keep skill instructions/rules concise.
- MUST keep `SKILL.md` frontmatter valid YAML: double-quote values containing `: `, else `skills` CLI silently skips skill. Verify `npx skills@latest add . --list` lists every `skills/*/SKILL.md`.

## Skill Evals

- MUST ship `evals/evals.json` with every skill, per `skill-creator` schema; fixtures under `evals/files/`.
- MUST write eval `prompt`s in Chinese (mirror real users); other eval fields English.
- MUST cover every branch and guardrail with ≥1 eval, each with checkable `expectations`.
- MUST target `expectations` at what skill adds: assert behavior model misses without skill, observable in output or transcript.
- MUST include ≥1 eval whose `prompt` triggers skill in natural language, no `/<skill>` command.
- MUST update evals in same change that alters skill behavior.

## Skill Workflow

Create/edit skill, or edit root `CLAUDE.md`/`AGENTS.md`, in this order; finish each step before next. Gate by trigger:

- User triggered step 1: after step 1, show draft and eval results, ask user to confirm, then run steps 2–7 unattended.
- Skill triggered step 1 (e.g. `self-improve`): run steps 1–7 unattended.
- Change touches only root `CLAUDE.md`/`AGENTS.md`: after edit, show diff, ask user to confirm, then run steps 2, 3, 5, 6 unattended; skip 4 and 7.

Unattended runs stop only where a step says ask user.

1. `/skill-creator`: draft/revise skill. Done when evals satisfy every Skill Evals rule.
2. `/writing-for-agents`: restructure and polish wording for agent readers. Done when every finding applied or rejected with reason.
3. `/caveman-compress`: apply its rules by hand to added/changed text only, leaving untouched lines as-is. Done when headings, code, URLs, and paths are unchanged.
4. `/skill-optimizer`: rerun evals with vs without skill on compressed text, fix misses and regressions. Done when every finding applied or rejected with reason and no eval regresses.
5. `/caveman-commit`: write Chinese message, then `git commit`.
6. Push: `git fetch origin`, `git rebase origin/<branch>` for linear history, then plain `git push`. Rebase conflicts in `CHANGELOG.md`: keep both sides, local entries on top; ask user on any other conflict. Push rejected: fetch, rebase, retry. Done when `HEAD` equals `origin/<branch>`.
7. Sync: refresh changed skills listed in `skills-lock.json` only, e.g. `./skillsw update foo bar -p -y`; if `setup-rules` changed, also run `/setup-rules update`. Copies are gitignored: commit in batches (`skills-lock.json`, then rules) per step 5, push per step 6. Done when every sync change is committed and `HEAD` equals `origin/<branch>`.

Steps 2–4 run only on agent-loaded files (`SKILL.md`, `references/*.md`, `rules/*.md`, root `CLAUDE.md`/`AGENTS.md`) added/modified in this change. Skill `AGENTS.md` generated from its `rules/`: edit `rules/`, rebuild.
