# 📚 The Reliability Suite Wiki

Welcome to the comprehensive knowledge base for the **API Reliability Suite**. This page aggregates everything you need to know about the design, technology, and operations of this platform.

---

## 🏗️ Technical Stack

We use a "Boring but Powerful" stack designed for 2026 enterprise standards.

| Component | Technology | Why? |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Type hints, performance, and vast ecosystem. |
| **Framework** | FastAPI | High performance, auto-validation, and Swagger UI. |
| **Validation** | Pydantic v2 | Strict data modeling and serialization. |
| **Linting** | Ruff | Blazing fast replacement for Flake8/Black/Isort. |
| **Logging** | Structlog | JSON-structured logging for observability. |
| **Tracing** | OpenTelemetry | Open standard for distributed tracing. |
| **Container** | Docker | Consistent deployment across environments. |

---

## 🏛️ Architecture & Design

We strictly follow **Hexagonal Architecture** (ADR-0001).

*   **[Read the Architecture Guide](architecture.md)**
*   **[View Decision Records (ADRs)](adr/0001-hexagonal-architecture.md)**

### Key Design Patterns used:
1.  **Repository Pattern**: `src/infrastructure/user_repository.py` hides database details.
2.  **Circuit Breaker**: `src/core/circuit_breaker.py` protects against cascading failures.
3.  **Dependency Injection**: FastAPI `Depends()` is used to inject Services into Controllers.

---

## 🛡️ Resilience Features

This API is designed to **fail gracefully**, never catastrophically.

1.  **Rate Limiting**:
    *   *Implementation*: Token Bucket Algorithm.
    *   *Limit*: 5 req/min for login, 60 req/min for general.
    *   *Goal*: Prevent DDoS and brute-force attacks.

2.  **Circuit Breakers**:
    *   *Behavior*: If upstream fails 5 times, we stop calling it for 60s.
    *   *Fallback*: Returns cached/degraded response instead of hanging.

3.  **Timeout Management**:
    *   All external calls have strict timeouts (e.g., 5 seconds) to prevent thread pool exhaustion.

---

## 🤖 AI & Automation

We employ an "AI-First" approach to operations.

*   **Automated Triage**: The system reads its own logs (`app.json`) -> sends them to an LLM -> returns a fix.
*   **Log Analysis**: See [ADR-0003](adr/0003-ai-error-analysis.md).
*   **CLI Debugger**: Run `make debug` to get an instant terminal report on system health.

---

## 📊 Operations Manual

How to run and monitor the system in production.

*   **[Setup Guide](setup.md)**: Deployment instructions (Local & Docker).
*   **[Observability Guide](observability.md)**: How to use Grafana and Jaeger.
*   **[API Reference](api-reference.md)**: List of available endpoints.

### Emergency Commands
| Scenario | Command |
| :--- | :--- |
| **System Down** | `make stack-down && make stack-up` |
| **Debug Logs** | `make debug` |
| **Run Tests** | `make test` |

---

## 🤝 Contribution Guidelines

1.  **Follow the Style**: Run `make format` before committing.
2.  **Add ADRs**: If you make a major design change, document it in `docs/adr/`.
3.  **Test First**: New features must include `pytest` coverage.
