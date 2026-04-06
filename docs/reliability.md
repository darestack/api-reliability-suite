# Reliability & Resilience Features

This suite demonstrates reliability patterns that help keep an API available, observable, and easier to debug under pressure.

---

## 🛡️ Circuit Breaker Demo
The **Circuit Breaker** pattern protects your system from cascading failures when external services (like databases or third-party APIs) go offline.

- **Fast Failure**: Instead of waiting for a slow timeout, the system quickly stops hammering a failing dependency.
- **Auto-Recovery**: After a cooldown period, the system automatically checks if the service is back online.
- **Current Fallback**: The demo endpoint returns a static degraded response when the breaker is open. It is not cache-backed yet.

!!! info "Implementation"
    See [Architecture & Internals](architecture.md#circuit-breakers) for the technical breakdown.

---

## 🚦 Traffic Control: Rate Limiting
To prevent abuse and ensure fair usage, we implement a **fixed-window** rate limiter via SlowAPI.

- **Login Protection**: Hardened against brute-force attacks.
- **Global Limits**: Prevents single users from exhausting server resources.
- **Storage**: `RATE_LIMIT_STORAGE_URI` controls the backend (Redis recommended for shared deployments).

!!! tip "Customization"
    Rate limits are environment-configurable via the `.env` file.

---

## 🤖 AI-Powered Triage
When an error occurs, the **AI summarizer** can analyze your logs to provide human-readable insights.

![AI Triage Screenshot](assets/ai-debug-screenshot.png)

- **Summarization**: Groups error patterns and surfaces likely causes based on log content.
- **Actionable Hints**: Offers suggested next steps from the LLM output.

!!! abstract "CLI Tool"
    You can trigger this analysis directly from your terminal using `make debug`.
