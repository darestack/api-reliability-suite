# API Reliability & Debugging Suite

 ![Thumbnail](docs/thumbnail.png)

 ![CI Pipeline](https://github.com/daretechie/api-reliability-suite/actions/workflows/ci.yml/badge.svg)
 ![Version](https://img.shields.io/badge/version-1.0.0-gold)
 ![Architecture](https://img.shields.io/badge/architecture-Hexagonal-orange)
 ![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)
 ![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688)
 [![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink)](https://github.com/sponsors/daretechie)

 ---

-## 😤 The Problem
-
-> **"Our API crashed at 3 AM and we have no idea why."**
->
-> **"This endpoint is slow, but we can't figure out where the bottleneck is."**
->
-> **"We're getting hammered by bots and can't stop them."**
-
-Sound familiar? Most APIs are built without proper **observability**, **security**, or **testing**—making debugging a nightmare.
-
-## ✅ The Solution
-
-This project is a **production-ready template** that shows you how to build APIs that are:
-
-- 🔍 **Observable** — Every request is traced, every error is logged in structured JSON
-- 🤖 **Intelligent** — Uses LLMs (Groq/OpenAI) to analyze logs and suggest fixes
-- 🛡️ **Secure** — Rate limiting & JWT authentication protect your resources
-- ✅ **Tested** — Automated tests catch bugs before they reach production
-- 🚀 **CI/CD Ready** — Push code, tests run automatically
-
----
-
+## �️ Architecture: Hexagonal (Ports & Adapters)
+
+This project follows **Hexagonal Architecture** to decouple business logic from infrastructure. This ensures the system remains testable, maintainable, and swap-able.
+
+```mermaid
+graph TD
+    subgraph "External World"
+        Client[Client Request]
+        Jaeger[Jaeger Tracing]
+        Prom[Prometheus]
+    end
+
+    subgraph "Infrastructure Adapters (Driving)"
+        API["FastAPI Entrypoint<br/>(src.main)"]
+    end
+
+    subgraph "Core Application (The Domain)"
+        direction TB
+        Service["Auth Service<br/>(src.services.auth_service)"]
+        Domain["Domain Models<br/>(src.domain.models)"]
+    end
+
+    subgraph "Infrastructure Adapters (Driven)"
+        Repo["User Repository<br/>(src.infrastructure.user_repository)"]
+        LLM["AI Adapter<br/>(src.core.llm)"]
+        Logger["Structlog Adapter<br/>(src.core.logging)"]
+    end
+
+    subgraph "Observability Sidecars"
+        OTel[OpenTelemetry Collector]
+        Metrics[Metrics Instrumentator]
+    end
+
+    Client --> API
+    API --> Service
+    Service --> Domain
+    Service --> Repo
+
+    API -.-> OTel
+    API -.-> Metrics
+    LLM -.-> API
+
+    OTel --> Jaeger
+    Metrics --> Prom
+```
+
+---
+
 ## �🎯 What This Demonstrates

 | Skill | Implementation |
 |-------|----------------|
+| **Architecture** | Hexagonal Architecture (Ports & Adapters) |
 | **API Development** | FastAPI with async endpoints |
+| **Traceability** | **Correlation IDs** + OpenTelemetry Tracing |
+| **Resilience** | **Circuit Breakers** (pybreaker) |
 | **Log Analysis (AI)** | Automated error triage via LLM (Groq/OpenAI/Google) |
 | **Structured Logging** | JSON logs via Structlog (ELK/Datadog ready) |
-| **Distributed Tracing** | OpenTelemetry instrumentation |
 | **Error Handling** | Global exception middleware |
 | **Rate Limiting** | Slowapi with IP-based throttling |
 | **Authentication** | JWT tokens with OAuth2 password flow |
-| **Configuration** | Environment-aware settings (Pydantic) |
+| **Configuration** | Environment-aware settings (**Strict Pydantic v2**) |
 | **Containerization** | Multi-stage Docker build |
 | **Automated Testing** | Pytest with async support |
 | **CI/CD** | GitHub Actions with matrix testing |
@@ -86,6 +134,7 @@
 | `GET /slow` | ❌ | ❌ | Simulates slow request (tracing demo) |
 | `POST /login` | ❌ | ❌ | Get JWT token (demo/secret123) |
 | `GET /protected` | ✅ | ❌ | Protected route (requires JWT) |
+| `GET /external-api` | ❌ | ❌ | **Circuit Breaker demo** (pybreaker) |
 | `GET /debug/summarize-errors`| ✅ | ❌ | **AI analyzes logs** and returns insights 🤖 |
 | `GET /metrics` | ❌ | ❌ | Prometheus metrics for Grafana 📊 |
 | `GET /force-error` | ❌ | ❌ | Triggers 500 error (error handling demo) |
@@ -172,6 +221,16 @@

 Using Pydantic Settings (`src/core/config.py`), the application enforces strict type validation on startup. If a required environment variable is missing, the app crashes immediately (Fail Fast) rather than failing silently at runtime.

+### 4. Correlation ID Propagation
+We use custom middleware (`src/core/middleware.py`) to inject a unique `X-Correlation-ID` into every request. This ID is propagated through all structured logs, allowing developers to stitch together the entire lifecycle of a request across different services and sidecars.
+
+### 5. Circuit Breaker Resilience
+Integrates the **Circuit Breaker** pattern (`src/core/circuit_breaker.py`) to prevent cascading failures. If an external service (like a 3rd party AI or Database) starts failing, the breaker "trips," immediately returning a fallback response and protecting the rest of the application from hanging.
+
+### 6. Strict Model Validation
+All domain models and configurations are enforced with **Pydantic v2 Strict Mode**. This ensures that "Garbage In, Garbage Out" is avoided at the boundary level, making runtime errors highly predictable.
+
 ---

 ## 👷 Developer Tools
