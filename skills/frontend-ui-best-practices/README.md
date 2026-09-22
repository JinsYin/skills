# frontend-ui-best-practices

Stack baseline, scaffolding and module documentation rules for React + shadcn/ui frontend
projects, 4 rules.

`SKILL.md` is only an index: each rule lives in its own file and is read on demand, and
`scripts/build.sh` compiles them into the full `AGENTS.md`.

## Scope

The engineering layer only: dependency choices, project scaffolding, style and token file
layout, module READMEs. The
interface layer — forms, overlays, lists, formats, icons — belongs to `ui-ux-best-practices`,
so that no rule exists as two copies that inevitably drift apart.

## Adding a rule

1. Copy `rules/_template.md` to `rules/<prefix>-<name>.md`.
2. Add one line to the rule index in `SKILL.md`.
3. Add the category to `rules/_sections.md` if it is new.
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

## Enabling

```bash
# from the repository root
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/frontend-ui-best-practices" \
      "$HOME/.claude/skills/frontend-ui-best-practices"
```

Symlink rather than copy — this repository stays the single source of truth.
