
## DevOps

### Development

- MUST follow the rules matched by `*-best-practices` skills.
- MUST slice development vertically by feature end-to-end: each slice implements one atomic capability across all necessary layers into a testable unit before starting the next; never slice horizontally across multiple features.
- Frontend implementations MUST build on code restored by `/design-to-code`, without adjusting styling or layout; if a required page, dialog, drawer, or component lacks code, MUST interview user to confirm style and layout.
- MUST add Chinese comments for non-obvious logic, constraints, public APIs, and test intent.
- Shell commands run in the login shell (zsh on macOS): quote globs and `=`-leading words (`--include='*.java'`, `echo '====='`; `[ ]` takes `=`, not `==`), write `${var}` before `[`, never name a variable `path` — zsh ties it to `PATH`, so later commands vanish and checks pass empty.

### Operation

- Dev env = root `docker-compose.yml` (deps) + `process-compose.yml` (processes); `process-compose -u .process-compose.sock up -D` only start command (`*.sock` in `.gitignore`). Every compose env var MUST have a default (never `${VAR:?err}`). Delivery = `deploy/` (Dockerfiles, Kustomize + Helm kept in parity) + `.drone.yml`, facts in `deploy/README.md`. Load `devops-best-practices` for every item below.
- Task adds first dependency service → same task creates both dev env files.
- Workflow step or task that runs the app starts, project has deps or processes but lacks either file → present backfill plan, ask: backfill first or skip. Skip holds for session.
- Delivery (containerize, CI, deploy to k8s, release) = own unit of work: interview → `deploy/README.md` → pipeline skeleton → one module per plan/ticket.
- Plan/ticket touching dev env or delivery files cites matching rules in its read-first list and puts `docker compose config -q` / `python3 deploy/scripts/k8s-parity.py` exiting 0 in its done criteria; final review checks both.

| Workflow | Backfill runs via | Delivery runs as |
|---|---|---|
| GSD | `gsdspec --quick` | new phase (`/gsd:add-phase`), then usual `gsdspec` chain |
| Matt | `/implement` quick task | No UI pipeline: `/to-spec` → `/to-tickets <spec>` |
| Addy | `incremental-implementation` quick slice | `spec-driven-development` (`spec/SPEC-delivery.md`) → `planning-and-task-breakdown` → `incremental-implementation` |
| Superpowers | current session, own commit | amend SPEC with Delivery chapter → `reviewed` → `writing-plans` appends phase to current milestone's `ROADMAP.md`; overrides fixed roadmap scope |
