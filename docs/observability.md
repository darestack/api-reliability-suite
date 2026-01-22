# Operations & Monitoring

This suite enables enterprise-grade observability out of the box, giving you full visibility into your API's health and performance.

## 1. Real-Time Dashboard (Grafana)

The suite includes a comprehensive Grafana Dashboard designed for SREs and Reliability Engineers. It provides immediate visibility into system health without requiring manual query construction.

![Grafana Dashboard](grafana-dashboard.png)

!!! abstract "Key Metrics"
    *   **SLO Tracking**: Monitors the Error Budget Burn Rate to detect reliability risks early.
    *   **Latency Distribution**: Tracks P99 Latency to ensure performance for tail-end users.
    *   **System Resilience**: Visualizes Circuit Breaker states in real-time.

!!! tip "Import Instructions"
    1.  Access Grafana at `http://localhost:3030`.
    2.  Navigate to **Dashboards** -> **New** -> **Import**.
    3.  Upload the configuration file: `infra/grafana/dashboard.json`.
    4.  Select **Prometheus** as the data source.

## 2. Distributed Tracing (Jaeger)

Every request is traced using OpenTelemetry.

=== "Incoming Traces"

    When a client hits `GET /health`, the app starts a trace. Middleware adds:

    *   `trace_id`: Global unique identifier.
    *   `span_id`: Identifier for this specific operation.
    *   `correlation_id`: A user-facing ID for support tickets.

=== "Outgoing Propagation"

    We use an **Instrumented HTTP Client** (`src/infrastructure/http_client.py`). When your API calls an external service (like OpenAI or Stripe), it automatically injects:

    *   `traceparent` header (W3C standard).
    *   `X-Correlation-ID` header.

    !!! info "Why this matters"
        This ensures you don't lose visibility when traffic leaves your network. You can trace a request from **Client -> API -> External Service** in a single view.

## 3. Resilience Patterns

### Circuit Breaker
Located in `src/core/circuit_breaker.py`.

!!! failure "Tripping the Circuit"
    If an external service fails **5 times in a row**, the breaker "trips" (Open state). Subsequent requests fail immediately (Fast Fail) or return cached data.

!!! success "Recovery (Half-Open)"
    After a **60s cooldown**, the breaker lets **one request** through. If it succeeds, the circuit closes and normal traffic resumes.

### Rate Limiting
Located in `src/core/rate_limit.py`. Implements the **Token Bucket** algorithm to protect endpoints like `/login` from brute-force attacks.
