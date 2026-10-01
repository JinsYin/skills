# Project Conventions

- MUST write skills in English.
- MUST keep instructions and rules in skills concise.
- MUST ship `evals/evals.json` with every skill, following the `skill-creator` schema; put fixtures under `evals/files/`.
- MUST write eval `prompt`s in Chinese to mirror real users, and all other eval fields in English.
- MUST cover every branch and guardrail with at least one eval, each with checkable `expectations`.
- MUST update evals in the same change that alters the skill's behavior.
