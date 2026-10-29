---
title: process-compose is the single entrypoint and starts docker compose first
impact: MEDIUM
impactDescription: two start commands → people and agents start app before deps healthy, then debug connection errors
tags: proc, process-compose, docker-compose, entrypoint
---

## process-compose is the single entrypoint and starts docker compose first

Two start commands (`docker compose up -d`, then `process-compose up`) → someone eventually runs only second: backend boots against absent database, error points at connection pool, not missing step. Agents especially start whatever last README line says.

`process-compose.yml` = only entrypoint. First process brings deps up, waits until healthchecks pass; every app process gates on it.

```yaml
processes:
  deps:
    # --wait (implies -d) blocks until every service healthcheck passes (rule compose-healthcheck-start-period);
    # --wait-timeout turns a dependency that never gets healthy into a failure instead of a hang
    command: "docker compose up --wait --wait-timeout 180"
    availability:
      restart: "no"          # one-shot (rule proc-oneshot-restart-no)

  backend:
    command: "./mvnw spring-boot:run"
    depends_on:
      deps:
        condition: process_completed_successfully
```

```bash
process-compose up -D      # whole stack, detached
process-compose down       # app processes only; dependency containers keep running
docker compose down        # stop dependencies explicitly (never -v unless resetting data)
```

Deps long-lived: `deps` defines no `shutdown` command, so `process-compose down` leaves containers and data running; next `up` fast. `--wait` treats service without `healthcheck` as ready once container runs, so app may connect before service accepts connections; give every default service healthcheck.
