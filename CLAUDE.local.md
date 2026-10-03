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

- Keep root `CHANGELOG.md` in Chinese per [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Log each notable change under `[Unreleased]` in the same commit; refactors go under `Changed`.
- Keep entries terse: one line each, what changed and its user-facing effect; omit implementation details, file lists and rationale.
- Cut versions only via `version-release`, which closes `[Unreleased]`.

### Development

- MUST follow the rules matched by `*-best-practices` skills.
- MUST add Chinese comments for non-obvious logic, constraints, public APIs, and test intent.

### Skills

- `skills-lock.json` is source of truth for installed skills, which may be gitignored. If it exists but `.agents/skills/` is missing (fresh clone, new worktree), restore before relying on skills: `./skillsw install`; without `skillsw`, `npx skills@latest experimental_install` (`.agents/skills/` only).

