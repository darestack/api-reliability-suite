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

    To spin up the full stack (API + Prometheus + Jaeger + Grafana):

    ```bash
    # Build and start all services
    make docker-build
    make stack-up
    ```

    **Service Registry:**

    | Service | URL | Login |
    |---------|-----|-------|
    | **API** | `http://localhost:8000` | — |
    | **Prometheus** | `http://localhost:9099` | — |
    | **Grafana** | `http://localhost:3030` | admin / admin |
    | **Jaeger** | `http://localhost:16686` | — |
    | **Redis** | `redis://localhost:6379` | — |

## Secrets and Redis (Production-Oriented)

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

## Verification

Run the hermetic test suite (does not require Docker).

```bash
make test
```
