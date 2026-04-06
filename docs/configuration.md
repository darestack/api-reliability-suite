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
SECRET_KEY=y0ur-5ecur3-k3y-h3r3
RATE_LIMIT_STORAGE_URI="redis://localhost:6379/0"
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
- [ ] **Shared Rate Limiting:** Use `RATE_LIMIT_STORAGE_URI` with Redis for distributed deployments.
- [ ] **Log Level Alignment:** Confirm `LOG_LEVEL` is set to `info` or `warning` for production stability.
- [ ] **LLM Connectivity:** Ensure at least one valid API key for an LLM provider is present in the `.env` file.
- [ ] **Tracing Setup:** Verify `OTLP_ENDPOINT` points to a valid collector if distributed tracing is required.
