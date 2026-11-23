
## GSD

- Prefer the `gsdspec` skill (`gsdspec --<mode>`) over calling `/gsd:*` directly.
- Once `spec-phase`, `discuss-phase`, `plan-phase`, `execute-phase`, `verify-work`, `code-review` or `debug` finishes and commits (direct or via `gsdspec`), invoke `self-improve`, clean runs too: its record Issue keeps below-gate observations later runs count toward weak gate.
- Record user prompts to `PROMPTS.md` upon completion of skills with source `open-gsd/gsd-core` or `jinsyin/skills` in `skills-lock.json` (including `gsdspec` and `gsd-*` skills).
