# Configuration Guide

This guide covers all configuration options available in the API Reliability Suite. The application uses **Pydantic Settings** for robust environment variable management and validation.

---

## 📄 Environment Variables

All settings can be configured via environment variables or a `.env` file in the project root.

### Core Application Settings

The following settings are defined in `src/core/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `"API Reliability Suite"` | Application name, used in logs and as the OpenTelemetry Service Name. |
| `DEBUG` | `False` | Enable debug mode. |
| `LOG_LEVEL` | `"info"` | Logging level (debug, info, warning, error, critical). |
| `SECRET_KEY` | `"change-me-in-production"` | Secret key used for JWT signing. **Must be changed for production!** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiration time in minutes. |

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
> The application automatically selects the available provider based on the keys provided.

---

## 🔧 Configuration Files

### `.env` File

Copy the provided example (if available) or create a `.env` file in the root directory:

```env
PROJECT_NAME="My Enterprise API"
LOG_LEVEL=debug
SECRET_KEY=y0ur-5ecur3-k3y-h3r3
GROQ_API_KEY=gsk_...
```

### Logging Configuration (`src/core/logging.py`)

Logging is pre-configured with the following defaults:
- **Format:** Structured JSON for files, human-readable console output.
- **Log File:** `app.json` (auto-rotated at 10MB, keeping 5 backups).
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
