# Configuration Guide

This guide covers all configuration options available in the API Reliability Suite. The application uses **Pydantic Settings** for robust environment variable management and validation.

---

## 📄 Environment Variables

All settings can be configured via environment variables or a `.env` file in the project root.
When `ENVIRONMENT` is set to `staging` or `production`, the app enforces a non-default `SECRET_KEY` and a shared `RATE_LIMIT_STORAGE_URI`.

### Core Application Settings

The following settings are defined in `src/core/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `"API Reliability Suite"` | Application name, used in logs and as the OpenTelemetry Service Name. |
| `ENVIRONMENT` | `"development"` | Deployment environment (`development`, `test`, `staging`, `production`). |
| `DEBUG` | `False` | Enable debug mode. |
| `LOG_LEVEL` | `"info"` | Logging level (debug, info, warning, error, critical). |
| `LOG_FILE_PATH` | `"app.json"` | Path to the structured log file used by the AI summarizer and file logging handler. |
| `DATABASE_URL` | `"sqlite+aiosqlite:///./data/reliability_suite.db"` | SQLAlchemy database URL. Use Postgres for shared or production-style environments. |
| `DATABASE_ECHO` | `False` | Enables SQLAlchemy SQL logging. |
| `SEED_DEMO_USER` | `True` | Seeds the demo admin account on startup for local runs. |
| `SECRET_KEY` | `"change-me-in-production"` | Secret key used for JWT signing. **Must be changed for production!** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiration time in minutes. |
| `RATE_LIMIT_STORAGE_URI` | `"memory://"` | Rate limit storage backend (use Redis in shared environments). |
| `RATE_LIMIT_HEADERS_ENABLED` | `False` | Adds standard rate limit headers to responses. |
| `RATE_LIMIT_IN_MEMORY_FALLBACK_ENABLED` | `False` | Allow in-memory fallback if storage is unavailable. |
| `RATE_LIMIT_KEY_PREFIX` | `"api-reliability-suite"` | Prefix for rate limit keys in shared storage. |
| `SETTINGS_SECRETS_DIR` | `None` | Optional secrets directory path (defaults to `/run/secrets` when present). |

### Observability Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OTLP_ENDPOINT` | `None` | The OTLP collector endpoint (e.g., `http://jaeger:4317`). If not set, traces are exported to the console. |
| `PROMETHEUS_BASE_URL` | `None` | Prometheus API base URL used by `/slo/report` to retrieve recording-rule values. |
| `CIRCUIT_BREAKER_CACHE_URL` | `None` | Redis URL for cache-backed circuit-breaker fallback payloads. |
| `CIRCUIT_BREAKER_CACHE_TTL_SECONDS` | `300` | TTL for the cached upstream payload returned during degraded fallback. |
| `SLO_TARGET_SUCCESS_RATIO` | `0.99` | Availability target used in SLO/error-budget reporting. |
| `SLO_TARGET_P99_LATENCY_SECONDS` | `1.0` | Latency objective used in SLO/error-budget reporting. |

### AI/LLM Provider Keys

To use the AI-powered CLI Debugger or the `/debug/summarize-errors` endpoint, you must provide **at least one** of the following keys:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `None` | OpenAI API Key. |
| `GROQ_API_KEY` | `None` | Groq API Key. |
| `GOOGLE_API_KEY` | `None` | Google AI (Gemini) API Key. |

> [!NOTE]
> The application automatically selects the first available provider in this order: `GROQ_API_KEY`, `OPENAI_API_KEY`, then `GOOGLE_API_KEY`.

---

## 🔧 Configuration Files

### `.env` File

Copy the provided example (if available) or create a `.env` file in the root directory:

```env
PROJECT_NAME="My Reliability Template"
ENVIRONMENT="development"
LOG_LEVEL=debug
LOG_FILE_PATH=app.json
DATABASE_URL="postgresql+asyncpg://app:app@localhost:5432/reliability_suite"
SECRET_KEY=y0ur-5ecur3-k3y-h3r3
RATE_LIMIT_STORAGE_URI="redis://localhost:6379/0"
CIRCUIT_BREAKER_CACHE_URL="redis://localhost:6379/1"
PROMETHEUS_BASE_URL="http://localhost:9099"
GROQ_API_KEY=gsk_...
```

### Logging Configuration (`src/core/logging.py`)

Logging is pre-configured with the following defaults:
- **Format:** Structured JSON for files, human-readable console output.
- **Log File:** Uses `LOG_FILE_PATH` (defaults to `app.json`) and rotates at 10MB, keeping 5 backups.
- **Enrichment:** Automatically includes `trace_id` and `span_id` for every log entry if a trace is active.

### Tracing Configuration (`src/core/tracing.py`)

Tracing is handled via OpenTelemetry:
- **Exporter:** OTLP (gRPC) if `OTLP_ENDPOINT` is set; otherwise, `ConsoleSpanExporter`.
- **Instrumentation:** Automatically instruments the FastAPI app.

---

## 🧪 Testing Configuration

The test suite uses its own configuration, often overriding settings in `tests/conftest.py` or via environment variables during the test run.

To run tests with code coverage:
```bash
make test
```

---

## 🚀 Quick Config Commands

```bash
# Verify current settings (dump)
python -c "from src.core.config import settings; print(settings.model_dump())"
```

## 🔐 Secrets Files

For Docker and Kubernetes deployments, you can provide secrets as files by mounting them under `/run/secrets` or setting `SETTINGS_SECRETS_DIR` to a custom path. Each secret file should be named after its setting, for example:

```text
/run/secrets/SECRET_KEY
/run/secrets/RATE_LIMIT_STORAGE_URI
```

---

## 📋 Production Readiness Standard

### Operational Configuration Audit
- [ ] **Secret Management:** Verify `SECRET_KEY` is not using the default value.
- [ ] **Persistent Identity Store:** Point `DATABASE_URL` at Postgres or another server-grade relational database for shared environments.
- [ ] **Shared Rate Limiting:** Use `RATE_LIMIT_STORAGE_URI` with Redis for distributed deployments.
- [ ] **Fallback Cache:** Configure `CIRCUIT_BREAKER_CACHE_URL` with Redis for cache-backed degraded responses.
- [ ] **Log Level Alignment:** Confirm `LOG_LEVEL` is set to `info` or `warning` for production stability.
- [ ] **LLM Connectivity:** Ensure at least one valid API key for an LLM provider is present in the `.env` file.
- [ ] **Tracing Setup:** Verify `OTLP_ENDPOINT` points to a valid collector if distributed tracing is required.
