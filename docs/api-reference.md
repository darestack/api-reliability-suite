# API Reference

!!! tip "Interactive Documentation"
    The API provides interactive Swagger UI docs (Requires running app locally).

    👉 **[Launch Swagger UI](http://localhost:8000/docs)**

## Endpoint Summary

| Endpoint | Method | Security | Resilience | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/health` | `GET` | Public | ✅ Rate Limit | Basic health check. Returns service status. |
| `/login` | `POST` | Public | ✅ Rate Limit | Exchange credentials for a **JWT Access Token**. |
| `/protected` | `GET` | **Bearer** | — | Example of a secure route requiring a valid token. |
| `/external-api` | `GET` | Public | ✅ **Circuit Breaker** | Proxy to external service. Demonstrates fallback logic. |
| `/debug/summarize-errors` | `GET` | **Bearer** | ✅ Rate Limit | **AI Agent endpoint**. Reads `app.json` logs and returns remediation. |
| `/slow` | `GET` | Public | — | Simulates high-latency request for **Tracing** demo. |
| `/force-error` | `GET` | Public | — | triggers a 500 error to test **Alerting**. |
