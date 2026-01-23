# Troubleshooting Guide

This guide covers common issues and diagnostic steps for the API Reliability Suite.

---

## 🚨 Common Startup Issues

### Port 8000 Already in Use
**Problem:** `make run` or `make docker-run` fails because the port is occupied.

**Solution:**
```bash
# Identify the process
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### LLM Provider Missing
**Problem:** AI Debugging (`make debug`) fails with "Provider not configured" or authentication errors.

**Solution:**
1.  Check your `.env` file for `GROQ_API_KEY`, `OPENAI_API_KEY`, or `GOOGLE_API_KEY`.
2.  Verify the keys are loaded:
    ```bash
    python -c "from src.core.config import settings; print(settings.model_dump())"
    ```

---

## 🔍 Observability Issues

### Traces Not Appearing in Jaeger
**Problem:** Traces are being printed to the console instead of appearing in the Jaeger UI.

**Solution:**
1.  Ensure the observability stack is up: `make stack-up`.
2.  Verify `OTLP_ENDPOINT` is set to `http://localhost:4317` in your environment.
3.  Check if the OTLP collector container is healthy:
    ```bash
    docker compose ps
    ```

### Missing Metrics in Grafana
**Problem:** Dashboards show "No Data".

**Solution:**
1.  Ensure you have made at least one request to the API: `curl http://localhost:8000/health`.
2.  Check if Prometheus is scraping the API: Open `http://localhost:9090/targets` and verify the `reliability-api` target is **UP**.

---

## 🛡️ Security & Authentication

### JWT Token Rejected (401 Unauthorized)
**Problem:** Requests to `/protected` or `/debug/summarize-errors` fail after login.

**Solution:**
1.  **Check Expiration:** Tokens expire in 30 minutes by default.
2.  **Verify Header:** Ensure the token is sent as a Bearer token:
    ```bash
    curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/protected
    ```

---

## 🐛 Diagnostic Commands

Use these commands for a rapid system audit:

| Task | Command |
|------|---------|
| **Linting Check** | `make lint` |
| **Logic Verification** | `make test` |
| **Full Cleanup** | `make clean` |
| **AI Triage Audit** | `make debug` |
| **Check Logs** | `cat app.json | jq .` |

---

## 📞 Reporting Issues

If an issue persists:
1.  Enable debug logs: Set `LOG_LEVEL=debug` in `.env`.
2.  Capture the relevant logs using `cat app.json | jq .`.
3.  Review the logs with the **AI Debugger** (`make debug`).
