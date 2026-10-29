# Project Conventions

## Core

- MUST write skills in English.
- MUST keep skill instructions/rules concise.
- MUST keep `SKILL.md` frontmatter valid YAML: double-quote values containing `: `, else `skills` CLI silently skips skill. Verify `npx skills@latest add . --list` lists every `skills/*/SKILL.md`.
- MUST interview user on anything unclear in attended sessions: ask focused questions interactively before acting on guess.

## Skill Workflow

Create/edit skill, or edit root `CLAUDE.md`/`AGENTS.md`: follow `write-great-skill` skill (source `skills/write-great-skill/`; installed copy may lag). Project additions:

- MUST write eval `prompt`s in Chinese (mirror real users); other eval fields English.
- Ship pushes via `git fetch origin`, `git rebase origin/<branch>` for linear history, then plain `git push`. Rebase conflicts in `CHANGELOG.md`: keep both sides, local entries on top; ask user on any other conflict. Push rejected: fetch, rebase, retry.
- Sync after Ship (post-merge when skill-triggered; skipped for root-doc-only change): refresh changed skills listed in `skills-lock.json` only, e.g. `./skillsw update foo bar -p -y`; if `setup-rules` changed, also run `/setup-rules update`. Copies are gitignored: commit in batches (`skills-lock.json`, then rules) and push as in Ship. Done when every sync change committed and `HEAD` equals `origin/<branch>`.
