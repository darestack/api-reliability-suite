# 1. Hexagonal Architecture

Date: 2026-01-22

## Status

Accepted

## Context

We are building a FastAPI service that will grow over time. We want the core business logic to stay testable and independent of framework or external-service details as the template matures.

## Decision

We adopt a **ports-and-adapters-inspired** layout:

- Request handling stays in FastAPI routes and middleware.
- Business logic lives in services and domain models.
- External integrations sit behind infrastructure adapters.
- Reliability concerns (tracing, logging, rate limiting, circuit breaking) are part of the application design.

## Consequences

### Positive
- **Testability:** Services and helper modules can be exercised without booting the full observability stack.
- **Refactor Path:** More boundaries can be promoted into explicit protocols or ports as the template grows.

### Negative
- **More Files:** A service layer adds indirection compared to a single-route script.
- **Discipline Required:** Adapters only help if they are kept thin and the seams are respected.