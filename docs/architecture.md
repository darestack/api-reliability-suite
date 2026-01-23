# Architecture & Internals

This project follows **Hexagonal Architecture** (Ports & Adapters). This design allows us to swap infrastructure (like switching from Groq to OpenAI) without touching our core business logic.

---

## 📐 System Diagram

```mermaid
graph TD
    subgraph "External World"
        Client[Client Request]
        Jaeger[Jaeger Tracing]
        Prom[Prometheus]
    end

    subgraph "Infrastructure Adapters (Driving)"
        API["FastAPI Entrypoint<br/>(src.main)"]
    end

    subgraph "Core Application (The Domain)"
        direction TB
        Service["Auth Service<br/>(src.services.auth_service)"]
        Domain["Domain Models<br/>(src.domain.models)"]
    end

    subgraph "Infrastructure Adapters (Driven)"
        Repo["User Repository<br/>(src.infrastructure.user_repository)"]
        LLM["AI Adapter<br/>(src.core.llm)"]
        Logger["Structlog Adapter<br/>(src.core.logging)"]
        HTTP["Instrumented HTTP Client<br/>(src.infrastructure.http_client)"]
    end

    subgraph "Observability Sidecars"
        OTel[OpenTelemetry Collector]
        Metrics[Metrics Instrumentator]
    end

    Client --> API
    API --> Service
    Service --> Domain
    Service --> Repo

    API -.-> OTel
    API -.-> Metrics
    LLM -.-> API
    HTTP -.-> OTel

    OTel --> Jaeger
    Metrics --> Prom
```

---

## 🛠️ The Codebase Explained

| Path | Feature | Why it matters |
| :--- | :--- | :--- |
| `src/core/middleware.py` | **Correlation ID** | Injects a unique `X-Correlation-ID` into every request for distributed tracing. |
| `src/core/config.py` | **Fail-Fast Settings** | Uses Pydantic v2 strict mode to validate environment variables on startup. |
| `src/core/circuit_breaker.py` | **Fault Tolerance** | Implementation of the Circuit Breaker pattern with state management (Open, Closed, Half-Open). |
| `src/core/rate_limit.py` | **Token Bucket** | Efficient, thread-safe rate limiting logic. |
| `src/services/` | **Hexagonal Services** | Framework-agnostic business logic. |
| `src/domain/models.py` | **Data Integrity** | Pydantic models ensuring "Garbage In" never reaches our core logic. |

---

## ⚡ Resilience Implementation

### Circuit Breakers
Our implementation tracks failures over a rolling window.
- **Trip Condition**: 5 consecutive failures.
- **Cooldown**: 60 seconds.
- **Metric**: Each state change is exported as a Prometheus metric for real-time monitoring.

### Trace Propagation
We implement **Context Propagation** in `src.infrastructure.http_client`. When calling external LLMs, the client automatically extracts the current trace context and injects it into the outgoing request headers.

!!! info "ADRs"
    For high-level design rationale, refer to the [Decision Log (ADRs)](adr/0001-hexagonal-architecture.md).
