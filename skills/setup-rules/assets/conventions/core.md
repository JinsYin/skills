# Agent Conventions

## Core

### Language

- Reply in Chinese while keeping AI terms untranslated.

### Safety

- Ask before delete or overwrite active edits.
- No reference external dirs unless told.

### Git

- Commit session changes only, slice vertical by feature.
- Use scoped Conventional Commits with Chinese descriptions, following `caveman-commit` skill rules if installed.
- Prefer fast-forward merge then `rebase` to keep history linear.
- Avoid `git reset --hard`.

### Changelog

- Keep root `CHANGELOG.md` using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Log each notable change in Chinese.
- Cut versions only via `version-release`, which closes `[Unreleased]`.

### Development

- MUST follow the rules matched by `*-best-practices` skills.
- MUST add Chinese comments for non-obvious logic, constraints, public APIs, and test intent.
- Shell commands run in the login shell (zsh on macOS): quote globs and `=`-leading words (`--include='*.java'`, `'====='`; `[ ]` takes `=`, not `==`), write `${var}` before `[`, never name a variable `path` — zsh ties it to `PATH`, so later commands vanish and checks pass empty.

### Skills

- `skills-lock.json` is source of truth for installed skills, which may be gitignored. If it exists but `.agents/skills/` is missing (fresh clone, new worktree), restore before relying on skills: `./skillsw clean install`; without `skillsw`, `npx skills@latest experimental_install` (`.agents/skills/` only).
