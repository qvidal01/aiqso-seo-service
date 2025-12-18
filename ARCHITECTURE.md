# Architecture

## Overview

AIQSO SEO Service is a multi-component system:

- **Backend API**: FastAPI application providing audit, client management, billing, and reporting APIs.
- **Workers**: Celery worker + beat scheduler for background processing (scheduled audits, score snapshots).
- **Dashboard**: Next.js UI that calls the backend API.
- **Rank Tracking**: SerpBear runs as a sidecar service and is accessed via its API.
- **Storage**: PostgreSQL is the primary datastore; Redis backs Celery.
- **Standalone tooling** (optional):
  - `src/core`: standalone auditor used by the CLI and MCP server.
  - `mcp_server`: Model Context Protocol server exposing audit tools.

## Runtime Components

### FastAPI (`app/`)

- Entry point: `app/main.py`
- Routers: `app/routers/*`
- Configuration: `app/config.py` (Pydantic Settings; reads environment variables)
- DB access: `app/database.py` + SQLAlchemy models under `app/models/*`

Startup behavior:
- Config validation runs in the application lifespan.
- Optional table creation via `DB_AUTO_CREATE` (see `docs/CONFIGURATION.md`).

### Celery (`app/celery_app.py`, `app/tasks.py`)

- Broker/backend: `REDIS_URL`
- Periodic scheduling: Celery Beat configuration in `app/celery_app.py`
- Scheduled jobs use the standalone auditor (`src/core/auditor.py`) and persist results to the database.

### Dashboard (`dashboard/`)

- Next.js app built and served independently.
- Primary config: `NEXT_PUBLIC_API_URL` to reach the FastAPI backend.

## Deployment

Primary deployment path is Docker Compose (`docker-compose.yml`):

- `postgres` + `redis` infrastructure services
- `backend` (FastAPI) + `celery-worker` + `celery-beat`
- `dashboard` (Next.js)
- `serpbear`

The backend container is built from `Dockerfile.backend` (recommended for Compose).

## Cross-Cutting Concerns

- **Configuration**: environment variables (optionally via `.env`).
- **Secrets**: never committed; use `.env` or secret manager. See `.env.example`.
- **Observability**: stdout logging with optional JSON logs (`LOG_JSON=true`).
- **Auth (optional hardening)**: `REQUIRE_API_KEY=true` enforces per-client API keys on most API routes.

