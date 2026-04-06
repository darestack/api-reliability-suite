# API Reliability Suite

Backend-focused FastAPI template with DevOps observability workflows and AI-assisted log triage.

![Thumbnail](docs/assets/thumbnail.png)

[![Documentation](https://img.shields.io/badge/docs-live-forestgreen)](https://daretechie.github.io/api-reliability-suite/)
[![CI Pipeline](https://github.com/daretechie/api-reliability-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/daretechie/api-reliability-suite/actions/workflows/ci.yml)
[![Security Policy](https://img.shields.io/badge/security-policy-blue)](SECURITY.md)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688)

Portfolio one-liner: Backend FastAPI service template that pairs DevOps observability with AI-assisted log triage.

## Why This Exists

Many FastAPI examples stop at routes and CRUD flows. This repository goes further by combining backend service patterns, DevOps reliability tooling, and AI-assisted debugging in a small runnable system.

## What's Included

This repository contains a working FastAPI application plus supporting local observability services.

Backend:

- JWT-based login and protected routes
- Separation between request handling, services, and infrastructure adapters
- Config-driven token expiry and request-level auth flow

DevOps:

- Route-level rate limiting with SlowAPI
- Prometheus metrics plus Grafana and Jaeger for local observability
- Circuit-breaker behavior for a demo upstream endpoint
- Structured logging with correlation IDs and trace context

AI:

- AI-assisted log summarization with Groq, OpenAI, or Google Gemini
- Runtime reporting of the active summarization provider
- Error-log filtering before summarization to keep the debugging path focused

## Requirements

- Python 3.12 or 3.13
- Poetry
- Docker with Compose support for the local observability stack

## Quickstart

```bash
git clone https://github.com/daretechie/api-reliability-suite.git
cd api-reliability-suite

make install
make run
```

The API will be available at `http://localhost:8000`.

Swagger UI is available at `http://localhost:8000/docs`.

For local exploration, a demo user is available:

- Username: `demo`
- Password: `secret123`

## Project Scope

This project is best treated as a template or reference implementation rather than a finished production system.

Current boundaries:

- `SECRET_KEY` defaults to a demo value and must be replaced for real deployments.
- Rate limiting uses in-memory storage by default unless `RATE_LIMIT_STORAGE_URI` is set (the Docker Compose stack uses Redis).
- `/external-api` returns a static degraded fallback when the breaker is open; it is not cache-backed.
- `/debug/summarize-errors` reads the configured log file and reports the runtime-selected provider.
- When `ENVIRONMENT` is set to `staging` or `production`, the app requires a non-default `SECRET_KEY` and a shared `RATE_LIMIT_STORAGE_URI`.

## Local Observability Stack

```bash
make stack-up
```

Services:

| Service    | URL                      |
| :--------- | :----------------------- |
| API        | `http://localhost:8000`  |
| Prometheus | `http://localhost:9099`  |
| Grafana    | `http://localhost:3030`  |
| Jaeger     | `http://localhost:16686` |
| Redis      | `redis://localhost:6379` |

Grafana default login: `admin / admin`

## Configuration

Create a `.env` file or export environment variables for the settings you want to override.

Common settings:

- `ENVIRONMENT`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `RATE_LIMIT_STORAGE_URI`
- `RATE_LIMIT_HEADERS_ENABLED`
- `RATE_LIMIT_KEY_PREFIX`
- `SETTINGS_SECRETS_DIR`
- `OTLP_ENDPOINT`
- `LOG_FILE_PATH`
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `GOOGLE_API_KEY`

The structured log file path defaults to `app.json`.
Docker and Kubernetes secret files are supported by setting `SETTINGS_SECRETS_DIR` (defaults to `/run/secrets` if present).

## API Overview

| Endpoint                  | Method | Purpose                                               |
| :------------------------ | :----- | :---------------------------------------------------- |
| `/health`                 | `GET`  | Health check with rate limiting                       |
| `/login`                  | `POST` | Exchange credentials for a JWT                        |
| `/protected`              | `GET`  | Example authenticated route                           |
| `/external-api`           | `GET`  | Circuit-breaker demo endpoint                         |
| `/debug/summarize-errors` | `GET`  | Summarize error logs with the configured LLM provider |
| `/slow`                   | `GET`  | Simulate latency for tracing demos                    |
| `/force-error`            | `GET`  | Trigger a 500 error for alerting and debugging demos  |

For more detail, see [API Reference](docs/api-reference.md).

## Development

```bash
make lint
make format
make test
```

Focused verification used for the recent hardening pass:

```bash
poetry run pytest -q --no-cov tests/test_auth.py tests/test_api_advanced.py tests/test_reliability.py tests/unit/core/test_llm_factory.py tests/unit/core/test_llm_summarizer.py tests/unit/core/test_google_provider.py tests/unit/core/test_openai_provider.py tests/unit/core/test_groq_provider.py
```

## Documentation

Live docs: <https://daretechie.github.io/api-reliability-suite/>

Run docs locally:

```bash
poetry run mkdocs serve
```

- [Architecture & Internals](docs/architecture.md)
- [Monitoring & Metrics](docs/observability.md)
- [Development Guide](docs/development.md)
- [Configuration Guide](docs/configuration.md)
- [Security Guide](docs/security.md)
- [Security Policy](SECURITY.md)
- [Production Checklist](docs/security.md)

This project was built with AI-assisted iteration for scaffolding, documentation, and test support, with manual review, correction, and verification of the final implementation.

## GitHub Metadata

Suggested repo description: Backend + DevOps + AI reliability template for FastAPI with auth, rate limiting, observability, circuit breaker, and log triage.

Suggested topics:
`fastapi` `backend` `devops` `observability` `opentelemetry` `prometheus` `grafana` `jaeger` `rate-limiting` `circuit-breaker` `jwt` `llm` `ai-ops`

## Support

- Documentation: <https://daretechie.github.io/api-reliability-suite/>
- Issues: <https://github.com/daretechie/api-reliability-suite/issues>
- Maintainer: [adelekedare2012@gmail.com](mailto:adelekedare2012@gmail.com) | [LinkedIn](https://linkedin.com/in/daretechie)
