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

### Postgres or Redis Port Collision in Docker Compose
**Problem:** `docker compose up` fails because `5432` or `6379` is already allocated.

**Solution:**
1.  Override the host ports when starting the stack:
    ```bash
    POSTGRES_PORT=15432 REDIS_PORT=16379 docker compose up -d
    ```
2.  Keep using the service names inside the Compose network. The API container still talks to `postgres:5432` and `redis:6379`.

### LLM Provider Missing
**Problem:** AI Debugging (`make debug`) fails with "Provider not configured" or authentication errors.

**Solution:**
1.  Check your `.env` file for `GROQ_API_KEY`, `OPENAI_API_KEY`, or `GOOGLE_API_KEY`.
2.  Verify the keys are loaded:
    ```bash
    python -c "from src.core.config import settings; print(settings.model_dump())"
    ```
3.  Confirm the log file configured by `LOG_FILE_PATH` exists and contains error events.

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
2.  Check if Prometheus is scraping the API: Open `http://localhost:9099/targets` and verify the `fastapi` target is **UP**.
3.  Open the provisioned dashboard directly at `http://localhost:3030/d/api-reliability-slo`.
4.  If the dashboard itself is missing, inspect Grafana provisioning logs:
    ```bash
    docker compose logs grafana
    ```

### Alerts Not Reaching Alertmanager
**Problem:** Prometheus rules fire, but no alerts appear in Alertmanager.

**Solution:**
1.  Verify the `alertmanager` container is running in `docker compose ps`.
2.  Open `http://localhost:9093` and confirm Alertmanager is reachable.
3.  Check the Prometheus configuration includes the `alertmanager:9093` target in `alerting.alertmanagers`.
4.  Confirm the alert rule has matched by checking `http://localhost:9099/alerts`.

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

### Admin Route Rejected (403 Forbidden)
**Problem:** `/debug/summarize-errors` returns `403` even with a valid token.

**Solution:**
1.  Confirm the authenticated user has the `admin` role in the configured database.
2.  If you are using the seeded local demo user, log in as `demo / secret123`.
3.  If you changed `DATABASE_URL`, verify the expected user record exists in that database.

---

## 🐛 Diagnostic Commands

Use these commands for a rapid system audit:

| Task | Command |
|------|---------|
| **Linting Check** | `make lint` |
| **Logic Verification** | `make test` |
| **Full Cleanup** | `make clean` |
| **AI Triage Audit** | `make debug` |
| **Smoke Load Test** | `make load-test` |
| **Check Logs** | `cat "${LOG_FILE_PATH:-app.json}" | jq .` |

---

## 📞 Reporting Issues

If an issue persists:
1.  Enable debug logs: Set `LOG_LEVEL=debug` in `.env`.
2.  Capture the relevant logs from `LOG_FILE_PATH` using `cat "${LOG_FILE_PATH:-app.json}" | jq .`.
3.  Review the logs with the AI triage tool (`make debug`).
