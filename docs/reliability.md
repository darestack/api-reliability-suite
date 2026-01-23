# Reliability & Resilience Features

This suite implements advanced patterns to ensure your API remains available, responsive, and easy to debug under pressure.

---

## 🛡️ Self-Healing: Circuit Breakers
The **Circuit Breaker** pattern protects your system from cascading failures when external services (like databases or third-party APIs) go offline.

- **Fast Failure**: Instead of waiting for a slow timeout, the system immediately returns a "Service Unavailable" error.
- **Auto-Recovery**: After a cooldown period, the system automatically checks if the service is back online.

!!! info "Implementation"
    See [Architecture & Internals](architecture.md#circuit-breakers) for the technical breakdown.

---

## 🚦 Traffic Control: Rate Limiting
To prevent DDoS attacks and ensure fair usage, we implement a **Token Bucket** rate limiter.

- **Login Protection**: Hardened against brute-force attacks.
- **Global Limits**: Prevents single users from exhausting server resources.

!!! tip "Customization"
    Rate limits are environment-configurable via the `.env` file.

---

## 🤖 AI-Powered Triage
When an error occurs, the **AI Agent** automatically analyzes your logs to provide human-readable insights.

![AI Triage Screenshot](assets/ai-debug-screenshot.png)

- **Root Cause Analysis**: Identifies exactly why a request failed (e.g., "Invalid API Key" vs "Database Timeout").
- **Actionable Advice**: Provides a step-by-step remediation plan for developers.

!!! abstract "CLI Tool"
    You can trigger this analysis directly from your terminal using `make debug`.
