# Backend, DevOps & AI Reliability Suite

![Thumbnail](assets/thumbnail.png)

[![CI Pipeline](https://github.com/daretechie/api-reliability-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/daretechie/api-reliability-suite/actions)
![Version](https://img.shields.io/badge/version-1.0.0-gold)
![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688)

---

## Why This Project Exists

Many API demos show the route layer but leave out the operational side of backend work. This project is designed to show how backend service structure, DevOps visibility, and AI-assisted debugging can fit together in one FastAPI codebase.

This suite is a **production-inspired FastAPI template** for studying reliability-focused APIs. It goes beyond a minimal tutorial, but it still expects hardening work before real production use.

## Core Themes

| Theme | Current implementation |
| :--- | :--- |
| **Backend** | JWT authentication, protected routes, service and infrastructure separation, and configuration-driven behavior. |
| **DevOps** | OpenTelemetry tracing, structured logs, Prometheus metrics, Grafana dashboards, Jaeger traces, rate limiting, and circuit-breaker behavior. |
| **AI** | LLM-based error summarization with Groq, OpenAI, and Google Gemini provider support. |

## Security and Hardening

See the production hardening checklist and secret-management guidance in the [Security Guide](security.md).

[Get Started](setup.md){ .md-button .md-button--primary } [View Architecture](architecture.md){ .md-button } [Development Guide](development.md){ .md-button }
