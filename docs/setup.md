# Setup Guide

## Installation

!!! warning "Prerequisites"
    - **Python 3.12+**
    - **Docker & Docker Compose**
    - **Poetry** (Recommended)

=== "Local Development"

    The fastest way to get started is using the `Makefile` (or Poetry directly).

    ```bash
    git clone https://github.com/daretechie/api-reliability-suite.git
    cd api-reliability-suite

    # Install dependencies and pre-commit hooks
    make install
    make install-hooks

    # Run the API locally
    make run
    ```

    The API will be available at [http://localhost:8000](http://localhost:8000).

=== "Docker Deployment"

    To spin up the full stack (API + Postgres + Redis + Prometheus + Alertmanager + Jaeger + Grafana):

    ```bash
    # Build and start all services
    make docker-build
    make stack-up

    # Apply the current database schema
    DATABASE_URL=postgresql+asyncpg://app:app@localhost:${POSTGRES_PORT:-5432}/reliability_suite poetry run alembic upgrade head
    ```

    **Service Registry:**

    | Service | URL | Login |
    |---------|-----|-------|
    | **API** | `http://localhost:8000` | — |
    | **Prometheus** | `http://localhost:9099` | — |
    | **Alertmanager** | `http://localhost:9093` | — |
    | **Grafana** | `http://localhost:3030` | admin / admin |
    | **Jaeger** | `http://localhost:16686` | — |
    | **Postgres** | `postgres://app:app@localhost:5432/reliability_suite` | app / app |
    | **Redis** | `redis://localhost:6379` | — |

    Grafana provisions the Prometheus data source and the `API Reliability SLO Overview` dashboard automatically. Open:

    - `http://localhost:3030`
    - `http://localhost:3030/d/api-reliability-slo`

    If Postgres or Redis already use their default host ports on your machine, override them when starting the stack:

    ```bash
    POSTGRES_PORT=15432 REDIS_PORT=16379 docker compose up -d
    ```

## Secrets, Postgres, and Redis (Production-Oriented)

### Secrets Directory

Pydantic Settings can load secrets from files by pointing `SETTINGS_SECRETS_DIR` to a directory (defaults to `/run/secrets` when present). Each secret file should contain a single value and be named after the setting key.

Example files:

```text
/run/secrets/SECRET_KEY
/run/secrets/RATE_LIMIT_STORAGE_URI
```

### Shared Rate Limit Storage

For distributed deployments, set `RATE_LIMIT_STORAGE_URI` to a shared Redis instance. The `limits` storage URI format supports `redis://host:port/db`.

Example:

```env
RATE_LIMIT_STORAGE_URI=redis://redis:6379/0
```

The CLI triage tool and `/debug/summarize-errors` both read from `LOG_FILE_PATH`, which defaults to `app.json`.

### Database and Fallback Cache

The app can run locally with SQLite, but the Compose stack demonstrates the intended shared backing services:

- `DATABASE_URL=postgresql+asyncpg://app:app@postgres:5432/reliability_suite`
- `RATE_LIMIT_STORAGE_URI=redis://redis:6379/0`
- `CIRCUIT_BREAKER_CACHE_URL=redis://redis:6379/1`

When `PROMETHEUS_BASE_URL` points to Prometheus, `/slo/report` also resolves the latest recording-rule values for SLO/error-budget reporting.

If you deploy behind a reverse proxy or ingress, also set:

- `TRUSTED_HOSTS` to your public API hostname(s)
- `CORS_ALLOW_ORIGINS` to the frontend origins that should call the API
- `HTTPS_REDIRECT_ENABLED=true` once TLS termination is in place

## Verification

Run the hermetic test suite (does not require Docker).

```bash
make test
```
