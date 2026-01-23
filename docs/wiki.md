# 📚 Developer Handbook & Wiki

This page serves as a high-density reference for the **Reliability Suite**. For detailed explanations, refer to the specific guides listed in the [Reference Index](#-reference-index).

---

## 🏗️ Technical Stack

| Component | Technology | Why? |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Performance, Type safety, Ecosystem. |
| **Framework** | FastAPI | Async-first, Auto-validation (Pydantic). |
| **Lint/Format** | Ruff | 100x faster than traditional tools. |
| **Logging** | Structlog | JSON production-ready logging. |
| **Observability** | OpenTelemetry | Vendor-neutral tracing standard. |

---

## 🚨 Emergency & Common Commands

| Scenario | Command |
| :--- | :--- |
| **Full Stack Start** | `make stack-up` |
| **Full Stack Stop** | `make stack-down` |
| **AI Log Analysis** | `make debug` |
| **Run Regression Tests** | `make test` |
| **Fix Linting/Format** | `make format` |

---

## 📖 Reference Index

- **[Architecture Deep Dive](architecture.md)**: Implementation of patterns and Hexagonal design.
- **[Reliability Features](reliability.md)**: Overview of Circuit Breakers, Rate Limiting, and AI Triage.
- **[Monitoring Guide](observability.md)**: How to use Grafana Dashboards and Jaeger Traces.
- **[Setup Guide](setup.md)**: Environment configuration and Docker setup.
- **[API Reference](api-reference.md)**: Interactive Swagger UI and endpoint details.

---

## 🤝 Contribution Rules

1. **Commit Style**: Use [Conventional Commits](https://www.conventionalcommits.org/).
2. **Quality Gates**: `make format` and `make test` must pass before any PR.
3. **ADRs**: Major design shifts require a new file in `docs/adr/`.
