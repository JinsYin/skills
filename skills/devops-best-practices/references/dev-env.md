# Dev Env: Create or Backfill

Local dev environment = root `docker-compose.yml` (long-lived stateful deps: DB, cache, MQ, object store) + root `process-compose.yml` (dev processes: backend, frontend, workers, one-shot build/migrate steps). `process-compose up -D` = only start command (rule `proc-deps-via-compose-wait`).

## When

- **Create**: current task introduces project's first dependency service → same task creates both files (with every existing runnable process) in its own change; no separate prompt.
- **Backfill**: project already has deps or runnable processes but lacks either file. Signs: README run steps, `scripts/*.sh` starting things, app config pointing at `localhost:5432`, `dev` script in `package.json`. Follow steps below.
  - Noticed while starting a workflow step or a task that runs the app → steps 1–5, asking at step 3.
  - User asked for dev env itself → steps 1, 2, 4, 5; request answers step 3.

## Backfill

1. **Detect.** Look for root `docker-compose.yml`/`compose.yaml` and `process-compose.yml`. Both present → no backfill; rule deviations (e.g. two start commands) go in plan as optional alignment, not blocker.
2. **Inventory from evidence.** Every row cites the file it came from.
   - Deps: datasource/cache/MQ/S3 URLs in app config (`application*.yml`, `.env.example`, `config/*`), driver dependencies (`pom.xml`, `package.json`), existing compose files under other names, README run steps.
   - Processes: runnable modules (Spring Boot plugin modules, `package.json` `dev`/`start` scripts, workers), build steps they need first (e.g. `mvn install` of a shared module), ports from config.
   - Unknown image version or port → ask.
3. **Present the plan, then ask.** Show:

   | Dep | Image:tag | Host port | Healthcheck | Evidence |
   |---|---|---|---|---|

   | Process | Command | Port | depends_on | Evidence |
   |---|---|---|---|---|

   plus files to create (`docker-compose.yml`, `process-compose.yml`, `.env.example`), docs whose run steps change (README, `CLAUDE.md` run section), verification below. Ask: **backfill first, or skip and continue**; wait for answer before writing any file. Skip → continue original task; answer stands for rest of session.
4. **Implement**: inside workflow via its quick path (convention names it), else directly; read `compose-*` and `proc-*` rules first.
5. **Verify from cold**, then commit backfill alone:

   ```bash
   docker compose config -q
   process-compose up -D
   # poll every process port / health endpoint until it answers, then:
   process-compose down
   ```

## Skeletons

```yaml
# docker-compose.yml
# Default: postgres + redis. Optional: --profile mq (rabbitmq). Ports/tags via .env (see .env.example).
services:
  postgres:
    image: ${BASE_REGISTRY:-docker.io}/library/postgres:${POSTGRES_TAG:-16}
    ports: ["${POSTGRES_HOST_PORT:-5432}:5432"]
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: CHANGE_ME
      POSTGRES_DB: app
    volumes: ["./docker/postgres/data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 20
      start_period: 30s
```

```yaml
# process-compose.yml — the only start command: process-compose up -D
version: "0.5"
processes:
  deps:
    command: "docker compose up --wait --wait-timeout 180"
    availability:
      restart: "no"
  backend:
    command: "./mvnw spring-boot:run"
    depends_on:
      deps:
        condition: process_completed_successfully
    readiness_probe:
      http_get: { host: 127.0.0.1, port: 8080, path: /actuator/health }
  frontend:
    command: "pnpm dev"
    working_dir: "./frontend"
    depends_on:
      backend:
        condition: process_healthy
```
