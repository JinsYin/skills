# Project Conventions

- Write skills in English.
- Commit messages: Conventional Commits with Chinese descriptions.

## Skill Workflow

Follow `write-great-skill` for creating or editing skills and root `CLAUDE.md`/`AGENTS.md`. Project additions:

- Eval `prompt`s in Chinese; other eval fields English.
- Ship: `git commit`, then `git push origin <branch>`.
- Sync, after Ship: `./sync.sh <changed-skills>`, then commit `skills-lock.json`.
