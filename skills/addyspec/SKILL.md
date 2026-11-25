---
name: addyspec
description: "Run addyosmani/agent-skills slash commands and local aliases as subcommands: /addyspec <spec|plan|build|quick|test|debug|review|code-simplify|ship|constraints|a11y|webperf> [args]."
disable-model-invocation: true
argument-hint: "<command> [args]"
---

# addyspec

`/addyspec <command> [args]` = [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) `/<command> [args]` + local skill aliases. `npx skills add` installs only that pack's skills; this skill vendors its commands and personas.

Snapshot: upstream `e997ac5` (2026-11-23).

## Dispatch

1. Split args: first word = command, rest = command's `$ARGUMENTS` (`/addyspec build auto` → `build`, `$ARGUMENTS` = `auto`). `planning` (upstream Gemini name) = `plan`.
2. Command missing or not in table → print table, ask user to pick.
3. Every skill in row's Skills column installed (in your available skills)? Any missing → stop, name them, print `npx skills add addyosmani/agent-skills`.
4. `local` row → read its `references/<command>.md` (if listed) and execute with `$ARGUMENTS`; else invoke row's skill directly with `$ARGUMENTS`. Upstream row → read `references/commands/<command>.md`, execute as upstream `/<command>`, per Adapter and Supplements.

| Command | Does | Skills | Personas |
|---|---|---|---|
| `spec` | `SPEC.md` (or delta `SPEC-<slug>.md`) before code | `spec-driven-development` | — |
| `plan` | Spec → `tasks/plan.md` + `tasks/todo.md` | `planning-and-task-breakdown` | — |
| `build` | Next task via TDD; `auto` = whole plan after one approval | `incremental-implementation`, `test-driven-development`, `planning-and-task-breakdown`, `debugging-and-error-recovery`, `doubt-driven-development` | — |
| `quick` | Quick slice logged under `tasks/quick/` (`local`, `references/quick.md`) | `incremental-implementation` | — |
| `test` | TDD; Prove-It for bugs | `test-driven-development`, `browser-testing-with-devtools` | — |
| `debug` | Root-cause debugging (`local`) | `debugging-and-error-recovery` | — |
| `review` | Five-axis code review | `code-review-and-quality`, `security-and-hardening`, `performance-optimization` | — |
| `code-simplify` | Simplify, behavior unchanged | `code-simplification`, `code-review-and-quality` | — |
| `ship` | Parallel persona fan-out → GO/NO-GO + rollback plan | `shipping-and-launch` | `code-reviewer`, `security-auditor`, `test-engineer` |
| `constraints` | Quality bar → `CONSTRAINTS.md`; `check` / `guard` / `ratchet` | `constraint-driven-development` | — |
| `a11y` | WCAG 2.2 AA audit | `accessibility-engineering` | `accessibility-auditor` |
| `webperf` | Core Web Vitals audit, web apps only | `performance-optimization` | `web-performance-auditor` |

## Adapter

Command files are upstream verbatim, written for Claude Code plugin install. Translate names; keep every step:

- `agent-skills:<name>` → installed skill `<name>`.
- `/<command>` inside command text (e.g. "run `/spec` first", "re-invoke `/build auto`") → `/addyspec <command>`.
- Persona subagent `<name>` (Agent tool `subagent_type`) → subagent whose instructions are `references/personas/<name>.md` plus inputs command lists. User-defined same-name agent (e.g. `.claude/agents/<name>.md`) wins. No subagent tool → run personas inline, one at a time; merge step unchanged.
- Upstream repo paths: `skills/<name>/…` → installed skill `<name>` dir; `references/<file>.md` → `references/shared/<file>.md` in any installed agent-skills skill.
- Other Claude Code names (`CLAUDE.md`, Agent tool, plan mode) → your harness's equivalent.

## Supplements

Local additions to upstream commands (preserved by `scripts/sync.sh`):

- **`spec`, `plan`** (incl. `build auto` Step 3): Interview user to confirm any unclear requirement before drafting or finalizing.
- **`build`**: If `tasks/plan.md` exists with unapproved status (not `Approved`/`In Progress`/`Completed`), update to `Approved` and commit `tasks/plan.md` alone before implementing (`build auto`: after Step 4 approval; fold into preparatory commit if Step 3 created plan).

## Sync

Maintainers refresh snapshot: `scripts/sync.sh [ref]` (default `main`) re-vendors commands, personas, `LICENSE`, rewrites Snapshot line, reports added/removed commands and each command's `agent-skills:` refs; align upstream rows to report, keep `local` rows and `references/<command>.md` unless upstream adds command.
