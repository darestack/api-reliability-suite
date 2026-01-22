# Architecture & Internals

This project follows **Hexagonal Architecture** (also known as Ports & Adapters) to ensure the system remains testable, maintainable, and decoupled from frameworks.

## System Diagram

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

## The Codebase Explained

A breakdown of the critical modules that provide reliability.

| Path | Feature | Why it matters |
|------|---------|----------------|
| `src/core/middleware.py` | **Correlation ID** | Injects a unique `X-Correlation-ID` into every request. This ID is propagated to logs and external services, allowing you to stitch together the entire story of a single request. |
| `src/core/config.py` | **Fail-Fast Settings** | Uses **Pydantic v2** strict mode to validate environment variables on startup. If a required key is missing, the application crashes immediately (safe) rather than failing efficiently at runtime. |
| `src/services/` | **Hexagonal Services** | The business logic lives here. It relies only on domain models and is completely unaware of HTTP, FastAPI, or JSON. This makes it trivially testable. |
| `src/domain/models.py` | **Rich Domain Models** | Uses Pydantic to ensure data integrity. "Garbage In" immediately results in a validation error, never "Garbage Out". |
