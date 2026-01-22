# API Reference

The API provides interactive documentation via Swagger UI.

👉 **[Launch Interactive Docs (Swagger UI)](http://localhost:8000/docs)** *(Requires running app locally)*

## Endpoint Summary

| Endpoint | Method | Auth? | Resilience | Description |
|----------|--------|-------|------------|-------------|
| `/health` | `GET` | ❌ | ✅ Rate Limit | Basic health check. Returns service status. |
| `/login` | `POST` | ❌ | ✅ Rate Limit | Exchange credentials for a JWT Access Token. |
| `/protected` | `GET` | ✅ | ❌ | Example of a secure route requiring a valid Bearer token. |
| `/external-api` | `GET` | ❌ | ✅ **Circuit Breaker** | Proxy to external service. Demonstrates fallback logic. |
| `/debug/summarize-errors` | `GET` | ✅ | ✅ Rate Limit | **AI Agent endpoint**. Reads `app.json` and analyzes errors. |
| `/slow` | `GET` | ❌ | ❌ | Simulates a high-latency request to demonstrate distributed tracing spans. |
| `/force-error` | `GET` | ❌ | ❌ | Intentionally raises a 500 error to test Exception Middleware and alerting. |
