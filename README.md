# API Reliability & Debugging Suite

![Thumbnail](docs/thumbnail.png)

![CI Pipeline](https://github.com/daretechie/api-reliability-suite/actions/workflows/ci.yml/badge.svg)
[![Documentation](https://img.shields.io/badge/docs-live-forestgreen)](https://daretechie.github.io/api-reliability-suite/)
![Version](https://img.shields.io/badge/version-1.0.0-gold)
![Architecture](https://img.shields.io/badge/architecture-Hexagonal-orange)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink)](https://github.com/sponsors/daretechie)

---

## 😤 The Reality

> **"Our API crashed at 3 AM and we have no idea why."**
> **"This endpoint is slow, but we can't figure out where the bottleneck is."**

Most APIs are built without proper **observability**, **security**, or **testing**—making debugging a nightmare when it matters most.

## ✅ The Solution

This suite is a **production-ready blueprint** for building "High-Reliability" APIs. It moves beyond basic tutorials to deliver an Enterprise-Grade Product.

### 🚀 Key Capabilities

| Feature | Description |
| :--- | :--- |
| **🔍 Observable** | Every request is traced via **OpenTelemetry**. Logs are structured (JSON) and correlated across services. |
| **🤖 Intelligent** | Integrated **AI Agent** (Groq/OpenAI) analyzes error logs and suggests root-cause fixes automatically. |
| **🛡️ Secure** | Enterprise protection patterns including **Rate Limiting** (Token Bucket) and **JWT Authentication**. |
| **🔗 Distributed** | **Trace Propagation** is built-in. Context is preserved from Client &rarr; API &rarr; External Services. |
| **💥 Resilient** | **Circuit Breakers** prevent cascading failures when downstream dependencies go offline. |
| **📊 Visual** | Includes a production-grade **Grafana Dashboard** for real-time SLO & Error Budget tracking.

---

## 🏛️ Architecture: Hexagonal (Ports & Adapters)

This project follows **Hexagonal Architecture** to decouple business logic from infrastructure. This ensures the system remains testable, maintainable, and swap-able.

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

## 📂 The Codebase Explained

Features you might miss if you don't look closely:

| Path | Feature | Why it matters |
|------|---------|----------------|
| `src/core/middleware.py` | **Correlation ID** | Injects `X-Correlation-ID` into every request. Connects logs across microservices. |
| `src/core/config.py` | **Fail-Fast Settings** | Uses **Pydantic v2** to validate env vars on startup. If a key is missing, the app crashes immediately (safe) rather than failing silently later. |
| `src/infrastructure/http_client.py` | **Distributed Tracing** | An instrumented client that automatically passes trace headers to external APIs (OpenAI, Stripe, etc). |
| `src/core/circuit_breaker.py` | **Circuit Breaker** | Tracks external failures. If an API is down, it "trips" and returns cached data instantly, preventing system hang. |
| `src/core/rate_limit.py` | **Token Bucket Limiter** | Prevents abuse by limiting requests per IP. |
| `src/services/` | **Hexagonal Logic** | Business logic is pure Python. It doesn't know what "FastAPI" is, making it easy to test. |

---

## 🚀 Day 2 Operations: Monitoring & Tracing

### 1. The "WOW" Dashboard (Real-Time)
We provide a pre-built Grafana Dashboard (`infra/grafana/dashboard.json`) that tracks:
*   **SLO Tracking**: Error Budget Burn Rate.
*   **Experience**: P99 Latency (the slowest 1% of requests).
*   **Resilience**: Live Circuit Breaker status.

**How to Import:**
1. Open Grafana (`http://localhost:3030` - admin/admin).
2. **Dashboards** → **New** → **Import**.
3. Upload `infra/grafana/dashboard.json`.
4. Select **Prometheus** datasource and Load.

![Grafana Dashboard](docs/grafana-dashboard.png)

### 2. Distributed Tracing (Jaeger)
See the lifecycle of every request.

1. **Spin up Infrastructure**: `docker compose up -d`
2. **Generate Traffic**: `make run` and hit endpoints.
3. **View Traces**: `http://localhost:16686`

---

### Run Full Stack (Recommended)
```bash
# Build image
make docker-build

# Start API + Prometheus + Jaeger + Grafana
make stack-up
```

### Stop All Services
```bash
make stack-down
```

---

## 🔍 API Endpoints

| Endpoint | Auth | Resilience | Description |
|----------|------|------------|-------------|
| `GET /health` | ❌ | ✅ Rate Limit | Health check |
| `GET /slow` | ❌ | ❌ | Simulates slow request (tracing demo) |
| `POST /login` | ❌ | ❌ | Get JWT token (demo/secret123) |
| `GET /protected` | ✅ | ❌ | Protected route (requires JWT) |
| `GET /external-api` | ❌ | ✅ **Circuit Breaker** | Demonstrates fault tolerance & fallback |
| `GET /debug/summarize-errors`| ✅ | ✅ Rate Limit | **AI analyzes logs** and returns insights 🤖 |
| `GET /metrics` | ❌ | ❌ | Prometheus metrics for Grafana 📊 |

---

## 🧠 AI-Powered Debugging
This project includes a **Self-Healing AI Agent** that reads `app.json` logs and provides actionable insights.

![AI Agent Screenshot](docs/assets/ai-debug-screenshot.png)

**How to use:**
1. Set an API key in `.env`: `GROQ_API_KEY`, `OPENAI_API_KEY`, or `GOOGLE_API_KEY`.
2. Hit the `/debug/summarize-errors` endpoint (requires auth).
3. Receive a JSON summary of root causes and fixes.

---

## 👷 Developer Tools

This project uses **Ruff** for linting and **Pre-Commit** for quality checks.

```bash
# Install git hooks (runs automatically on commit)
make install-hooks

# Run tests
make test

# Format code manually
make format
```

---

## 💖 Support This Project

If this template helps you, consider [sponsoring my work](https://github.com/sponsors/daretechie)!

## 🤝 Hire Me

Looking for a developer who understands **API reliability, security, and DevOps**?
📧 [adelekedare2012@gmail.com](mailto:adelekedare2012@gmail.com) | [LinkedIn](https://linkedin.com/in/daretechie)
