# Shop

## Run locally

1. Start PostgreSQL 16 yourself on port 5432 (db/user `shop`, password `shop`).
2. Start Redis 7 on port 6379.
3. `cd backend && mvn spring-boot:run` (port 8080).
4. `cd frontend && pnpm install && pnpm dev` (port 5173).
