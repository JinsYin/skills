# ui-ux-best-practices

UI and interaction rules for Chinese-language admin consoles (React or Vue), 24 rules in 6
categories.

`SKILL.md` is only an index: each rule lives in its own file and is read on demand, and
`scripts/build.sh` compiles them into the full `AGENTS.md`.

## Impact levels

Backend rules can be graded by "breaks the build / is a bug". UI problems rarely crash
anything — they make users do the wrong thing. So the grading here is by **user consequence**:

| Level | Meaning | Categories |
|---|---|---|
| CRITICAL | Data loss or an irreversible wrong action | `overlay-` |
| HIGH | The user cannot finish the task, or is misled | `form-` `list-` |
| MEDIUM | Doable, at extra cognitive cost | `format-` |
| LOW | Inconsistent look and feel | `consistency-` `console-` |

Overlays rank highest not because they are written most often, but because a delete without
confirmation and a form that keeps its state after closing both produce unrecoverable data
outcomes, and neither reproduces easily in manual testing.

## Rule style

One rule per file, each stating what to do **and why**: an imperative whose consequence is
never stated gets followed inconsistently.

Organization-specific facts — email domain, logo size, header composition — are part of this
ruleset rather than being left out. A project may override any of them in its own `CLAUDE.md`.

## Adding a rule

1. Copy `rules/_template.md` to `rules/<prefix>-<name>.md`.
2. Add one line to the matching section of the rule index in `SKILL.md`.
3. Update the rule count in the category table.
4. Rebuild: `bash scripts/build.sh`.

Always verify that index and rule files still match — this is the only silent failure of this
layout:

```bash
index_file="$(mktemp)"
rules_file="$(mktemp)"
trap 'rm -f "$index_file" "$rules_file"' EXIT
grep -oE '^- `[a-z]+-[a-z-]+`' SKILL.md | tr -d '`' | sed 's/^- //' | sort > "$index_file"
ls rules/[a-z]*.md | xargs -n1 basename | sed 's/\.md$//' | sort > "$rules_file"
diff "$index_file" "$rules_file" && echo OK
```

`scripts/build.sh` takes the document title from the H1 of `SKILL.md`, so adding or renaming a
rule never requires editing the script.

## Enabling

```bash
# from the repository root
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/ui-ux-best-practices" \
      "$HOME/.claude/skills/ui-ux-best-practices"
```

Symlink rather than copy — this repository stays the single source of truth.
