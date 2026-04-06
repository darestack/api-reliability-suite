# Development Guide

This guide covers the technical setup, project structure, and workflow for the API Reliability Suite.

---

## 🛠️ Development Setup

### Prerequisites

- **Python 3.12+**
- **Poetry** (Mandatory for dependency management)
- **Docker & Docker Compose** (For observability stack)
- **Make** (Optional, but recommended for task automation)

### Initial Setup

```bash
# 1. Install dependencies
make install

# 2. Set up pre-commit hooks
make install-hooks

# 3. Configure environment
cp .env.example .env

# 4. Start the observability stack (Prometheus, Jaeger, Grafana)
make stack-up
```

### Development Workflow

| Command | Description |
|---------|-------------|
| `make run` | Starts the FastAPI server with hot-reload (`0.0.0.0:8000`). |
| `make test` | Runs the full test suite with coverage report. |
| `make lint` | Runs Ruff check on the codebase. |
| `make format` | Runs Ruff format on the codebase. |
| `make debug` | Runs the AI-powered CLI log triage tool against `LOG_FILE_PATH`. |

---

## 🏗️ Project Structure

The project uses a **service layer plus adapters** layout to keep request handling, business logic, and integrations separated.

```
src/
├── core/            # Framework-level logic (logging, tracing, auth, config)
├── domain/          # Pure business models (Pydantic schemas)
├── infrastructure/  # External adapters (persistence, external clients)
├── services/        # Business logic orchestration
└── main.py          # Application assembly and startup
```

---

## 🔧 Extending the API

### Adding a New Endpoint

1.  **Define the Schema:** Add a Pydantic model in `src/domain/models.py`.
2.  **Logic Separation:** If the endpoint involves business logic, implement it in a service within `src/services/`.
3.  **Infrastructure:** If you need to interact with a database or external API, add an adapter in `src/infrastructure/`.
4.  **Route Registration:** Add the endpoint in `src/main.py`.

---

## 🧪 Testing

The project uses `pytest` for all testing. Coverage targets are set to ensure reliability.

### Test Files
- `tests/conftest.py`: Shared fixtures (FastAPI client, dummy tokens).
- `tests/test_api.py`: Integration tests for main endpoints.
- `tests/test_auth.py`: Security and JWT logic verification.
- `tests/test_reliability.py`: Verification of Circuit Breaker and Rate Limiting.

### Running Tests
```bash
# Run all tests
make test

# Run a specific test file
poetry run pytest tests/test_reliability.py
```

---

## 🔍 Debugging & Analysis

### AI-Powered CLI Debugger
Run `make debug` to trigger an automated analysis of the configured `LOG_FILE_PATH`. This tool filters for error events and uses an LLM to provide:
1.  **Summary:** A human-readable explanation of why the crash happened.
2.  **Remediation:** Actionable steps to fix the issue.

### Log Inspection
Logs are structured as JSON in the file configured by `LOG_FILE_PATH` (`app.json` by default). You can use `jq` to analyze them:
```bash
# View only error logs
cat "${LOG_FILE_PATH:-app.json}" | jq 'select(.level == "error")'

# Trace a request by correlation_id
cat "${LOG_FILE_PATH:-app.json}" | jq 'select(.correlation_id == "your-id")'
```

---

## 🚀 Deployment

The project is containerized and ready for Kubernetes. See [Deployment Guide](deployment.md) for details on the `infra/k8s` manifests.
