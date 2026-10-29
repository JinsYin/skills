# backfill-prototype eval fixtures

Each fixture holds `steps/NN-<slug>/` overlays, slugs in English kebab-case; the commit message is the slug with dashes as spaces. Build a run copy with real git history:

```sh
cp -R evals/files/<fixture> "${tmp}" && sh evals/files/init.sh "${tmp}"
```

Steps apply in order, one commit each; the last step is the working tree the prompt runs in. Give the with-skill run the skill at `${tmp}/.claude/skills/backfill-prototype/`.

Regenerate with `python3 evals/gen_fixtures.py evals/files`.
