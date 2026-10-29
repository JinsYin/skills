
## DevOps

- Dev env = root `docker-compose.yml` (deps) + `process-compose.yml` (processes); `process-compose up -D` only start command. Delivery = `deploy/` (Dockerfiles, Kustomize + Helm kept in parity) + `.drone.yml`, facts in `deploy/README.md`. Load `devops-best-practices` for every item below.
- Task adds first dependency service → same task creates both dev env files.
- Workflow step or task that runs the app starts, project has deps or processes but lacks either file → present backfill plan, ask: backfill first or skip. Skip holds for session.
- Delivery (containerize, CI, deploy to k8s, release) = own unit of work: interview → `deploy/README.md` → pipeline skeleton → one module per plan/ticket.
- Plan/ticket touching dev env or delivery files cites matching rules in its read-first list and puts `docker compose config -q` / `python3 deploy/scripts/k8s-parity.py` exiting 0 in its done criteria; final review checks both.

| Workflow | Backfill runs via | Delivery runs as |
|---|---|---|
| GSD | `gsdspec --quick` | new phase (`/gsd:add-phase`), then usual `gsdspec` chain |
| Matt | `/implement` quick task | No UI pipeline: `/to-spec` → `/to-tickets <spec>` |
| Superpowers | current session, own commit | amend SPEC with Delivery chapter → `reviewed` → `writing-plans` appends phase to current milestone's `ROADMAP.md`; overrides fixed roadmap scope |
