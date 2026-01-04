# API Reliability & Debugging Suite

![CI Pipeline](https://github.com/daretechie/api-reliability-suite/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink)](https://github.com/sponsors/daretechie)

---

## 😤 The Problem

> **"Our API crashed at 3 AM and we have no idea why."**
>
> **"This endpoint is slow, but we can't figure out where the bottleneck is."**
>
> **"We're getting hammered by bots and can't stop them."**

Sound familiar? Most APIs are built without proper **observability**, **security**, or **testing**—making debugging a nightmare.

## ✅ The Solution

This project is a **production-ready template** that shows you how to build APIs that are:

- 🔍 **Observable** — Every request is traced, every error is logged in structured JSON
- 🛡️ **Secure** — Rate limiting & JWT authentication protect your resources
- ✅ **Tested** — Automated tests catch bugs before they reach production
- 🚀 **CI/CD Ready** — Push code, tests run automatically

---

## 🎯 What This Demonstrates

| Skill | Implementation |
|-------|----------------|
| **API Development** | FastAPI with async endpoints |
| **Structured Logging** | JSON logs via Structlog (ELK/Datadog ready) |
| **Distributed Tracing** | OpenTelemetry instrumentation |
| **Error Handling** | Global exception middleware |
| **Rate Limiting** | Slowapi with IP-based throttling |
| **Authentication** | JWT tokens with OAuth2 password flow |
| **Configuration** | Environment-aware settings (Pydantic) |
| **Containerization** | Multi-stage Docker build |
| **Automated Testing** | Pytest with async support |
| **CI/CD** | GitHub Actions with matrix testing |

---

## 🚀 Quick Start

### Local Development
```bash
git clone https://github.com/daretechie/api-reliability-suite.git
cd api-reliability-suite
poetry install
poetry run uvicorn src.main:app --reload
```

### Run with Docker
```bash
docker build -t reliability-suite .
docker run -p 8000:8000 reliability-suite
```

---

## 🔍 API Endpoints

| Endpoint | Auth | Rate Limited | Description |
|----------|------|--------------|-------------|
| `GET /health` | ❌ | ✅ 5/min | Health check |
| `GET /slow` | ❌ | ❌ | Simulates slow request (tracing demo) |
| `POST /login` | ❌ | ❌ | Get JWT token (demo/secret123) |
| `GET /protected` | ✅ | ❌ | Protected route (requires JWT) |
| `GET /force-error` | ❌ | ❌ | Triggers 500 error (error handling demo) |
| `GET /docs` | ❌ | ❌ | Interactive Swagger docs |

---

## 📡 Observability & Tracing

This suite supports **OTLP (OpenTelemetry Line Protocol)** for production-grade tracing. 

### Connecting to Jaeger
To see your traces in a dashboard, update your `.env`:
```env
OTLP_ENDPOINT="http://localhost:4317"
```
Then run Jaeger via Docker:
```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest
```
View your traces at `http://localhost:16686`.

---

## 🧠 Roadmap: AI-Powered Debugging

- 🤖 **LLM-Powered Log Analysis** — Auto-summarize error patterns
- 🔮 **Predictive Alerts** — Detect anomalies before they become incidents
- 💬 **Natural Language Queries** — "Show me all slow requests from yesterday"

---

## 💖 Support This Project

If this template helps you, consider [sponsoring my work](https://github.com/sponsors/daretechie)!

## 🤝 Hire Me

Looking for a developer who understands **API reliability, security, and DevOps**?  
📧 [adelekedare2012@gmail.com](mailto:adelekedare2012@gmail.com) | [LinkedIn](https://linkedin.com/in/daretechie)