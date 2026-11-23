---
title: process-compose uses unix domain socket to prevent port conflicts
impact: MEDIUM
impactDescription: default port 9876 conflicts across concurrent projects and crashes background daemon silently
tags: proc, process-compose, socket, uds, port-conflict
---

## process-compose uses unix domain socket to prevent port conflicts

`process-compose` defaults to TCP port 9876 for its internal REST API server. When running multiple projects concurrently on the same machine, subsequent projects fail on startup:

`FTL start http server on localhost:9876 failed error="listen tcp 127.0.0.1:9876: bind: address already in use"`

In detached mode (`-D`), the CLI exits 0 immediately while the background daemon crashes, misleading agents and developers into thinking the stack started.

Bind `process-compose` to a project-scoped Unix domain socket instead of a global TCP port:

```bash
process-compose -u .process-compose.sock up -D      # start stack detached
process-compose -u .process-compose.sock down       # stop stack
process-compose -u .process-compose.sock process list
```

Alternatively, set `PC_SOCKET_PATH=.process-compose.sock` in the shell or `.envrc` (`direnv`).

**Ignore socket file in Git:**
Runtime socket files are ephemeral machine-local endpoints and must never be tracked. Add `*.sock` to `.gitignore`:

```gitignore
*.sock
```

**Pitfalls to avoid:**
- **Do not use `--no-server`:** Disabling the HTTP server prevents port conflicts but breaks IPC completely—`process-compose down`, `attach`, and `process restart` will fail.
- **Do not use `-U` without path:** Bare `-U` creates `/tmp/process-compose-<pid>.sock` using the current client PID. A subsequent `process-compose -U down` runs under a different PID and fails to find the socket. Always specify a fixed path via `-u` or `PC_SOCKET_PATH`.
