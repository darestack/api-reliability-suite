# Architecture & Internals

This project uses a service-oriented layout with **ports-and-adapters-inspired seams**. Some boundaries are formalized through abstractions such as `BaseLLM`, while others are still concrete implementations that can be refactored further as the template matures.

The goal is practical separation rather than architecture theater:

- Request handling stays in FastAPI routes and middleware.
- Business logic lives in services and domain models.
- External integrations sit behind infrastructure adapters or provider abstractions.
- Reliability concerns such as tracing, logging, rate limiting, and circuit breaking are treated as part of the application design, not bolt-ons.

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
        LLM["AI Adapter<br/>(src.core.llm/)"]
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

## Design Principles

### Service Layer + Adapter Seams

We decouple the core decision-making paths from the external systems they depend on.

Why it helps:

- **Testability:** Services and helper modules can be exercised without booting the full observability stack.
- **Provider Switching:** Moving between supported LLM providers is mostly a configuration and adapter concern.
- **Refactor Path:** More boundaries can be promoted into explicit protocols or ports as the template grows.

### Reliability as a First-Class Concern

Observability and failure handling are part of the runtime design, not just deployment garnish.

Current examples in the codebase:

- **Distributed Tracing:** Requests carry correlation metadata and export spans when `OTLP_ENDPOINT` is configured.
- **Circuit Breaker:** The demo upstream path fails fast after repeated errors and returns a degraded fallback response.
- **AI Log Triage:** The summarizer reads filtered local error logs and produces a first-pass explanation plus remediation hints.

---

## 🛠️ The Codebase Explained

| Path | Feature | Why it matters |
| :--- | :--- | :--- |
| `src/core/middleware.py` | **Correlation ID** | Injects a unique `X-Correlation-ID` into every request for distributed tracing. |
| `src/core/config.py` | **Fail-Fast Settings** | Uses Pydantic v2 strict mode to validate environment variables on startup. |
| `src/core/circuit_breaker.py` | **Fault Tolerance** | Implementation of the Circuit Breaker pattern with state management (Open, Closed, Half-Open). |
| `src/core/rate_limit.py` | **Fixed-Window Rate Limiting** | SlowAPI + limits with configurable storage backend. |
| `src/services/` | **Service Layer** | Business logic orchestration that stays separate from request handling. |
| `src/domain/models.py` | **Data Integrity** | Pydantic models ensuring "Garbage In" never reaches our core logic. |

---

## ⚡ Resilience Implementation

### Circuit Breakers
Our implementation tracks consecutive failures.
- **Trip Condition**: 5 consecutive failures.
- **Cooldown**: 60 seconds.
- **Metric**: Each state change is exported as a Prometheus metric for real-time monitoring.

### Trace Propagation
We provide an **instrumented HTTP client** in `src.infrastructure.http_client` that propagates trace context and correlation IDs for outbound calls.

!!! info "ADRs"
    For high-level design rationale, refer to the [Decision Log (ADRs)](adr/0001-hexagonal-architecture.md).
