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
| `/external-api` | `GET` | Public | ✅ **Circuit Breaker** | Proxy to external service. When open, returns the latest cached upstream payload if fallback caching is configured. |
| `/debug/summarize-errors` | `GET` | **Bearer (Admin)** | ✅ Rate Limit | Reads the configured log file, returns an AI summary, reports the runtime-selected provider, and records which admin requested it. |
| `/slo/report` | `GET` | Public | ✅ **SLO Reporting** | Returns SLO targets and, when `PROMETHEUS_BASE_URL` is configured, the latest Prometheus recording-rule values. |
| `/slow` | `GET` | Public | — | Simulates high-latency request for **Tracing** demo. |
| `/force-error` | `GET` | Public | — | triggers a 500 error to test **Alerting**. |
