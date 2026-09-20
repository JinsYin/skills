# Sensitive-file access controls

## Rules

- Protect every project file named `.env`, `.env.dev`, `.env.test`, or `.env.prod`; remove the set only by explicit opt-out. Accept explicit project-relative files/directories; directories are recursive.
- Use the default file names exactly as written; never prefix them with `/` or `./`.
- Normalize extra paths, reject absolute paths and `..`, and enumerate nonportable globs. If a native control cannot express the patterns and exception exactly, stop and report the gap.
- Inspect metadata/config only. Never read, print, diff, stage, hash, or send protected contents.
- Merge native controls; preserve unrelated or stricter settings. Stop on incompatible policy.
- Warn if a protected file is tracked or in Git history; denial does not remove history.
- Rules/prompts are not access controls.

Native mappings use each default file name unchanged.

## Agent mapping

### Codex

Use `.codex/config.toml`. Add each deny to the active profile; for a new config:

```toml
default_permissions = "project-edit"

[permissions.project-edit]
extends = ":workspace"

[permissions.project-edit.filesystem.":workspace_roots"]
"<file>" = "deny"
```

Stop before changing legacy, `danger-full-access`, or managed permission postures. Applies to new sessions.

### Claude Code

In `.claude/settings.json`, merge `permissions.deny += "Read(<file>)"` and sandbox `filesystem.denyRead += "<file>"`; keep `sandbox.enabled=true` and `allowUnsandboxedCommands=false`.

### Cursor

Merge `<file>` into `.cursorignore` and `permissions.deny += "Read(<file>)"` into `.cursor/cli.json` (preserve/ensure `permissions.allow`). Warn that terminal and MCP access can bypass these controls.

### Antigravity

Merge `<file>` into `.gitignore`. Require project Strict Mode and project read denial in desktop/IDE; list these external settings for confirmation. For every active CLI profile, merge `permissions.deny += "read_file(<file>)"` into `settings.json`. If UI/profile access is unavailable, report it unresolved.

Apply the mapping to each default entry and every selected path.

## Validate

- Parse changed JSON/TOML and run available offline config-load checks.
- Test all default entries in `.gitignore` and `.cursorignore`.
- Review changed/external targets without asking an Agent to access a protected file.
