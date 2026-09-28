# Agent Conventions

## Core

### Language

- Reply in Chinese while keeping AI terms untranslated.

### Safety

- Ask before delete or overwrite active edits.
- No reference external dirs unless told.

### Git

- Commit session changes only, slice vertical by feature.
- Use scoped Conventional Commits spec, Chinese descriptions.
- Avoid `git reset --hard`.
- Prefer fast-forward merge then `rebase` to keep history linear.

### Changelog

- Keep root `CHANGELOG.md` in Chinese per [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Log each notable change under `[Unreleased]` in the same commit; refactors go under `Changed`.
- Cut versions only via `version-release`, which closes `[Unreleased]`.

### Development

- MUST follow the rules matched by `*-best-practices` skills.
- MUST add Chinese comments for non-obvious logic, constraints, public APIs, and test intent.

