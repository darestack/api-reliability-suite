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

## Verification

Run the hermetic test suite (does not require Docker).

```bash
make test
```
