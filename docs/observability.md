# Operations & Monitoring

This suite enables enterprise-grade observability out of the box, giving you full visibility into your API's health and performance.

## 1. The "WOW" Dashboard (Grafana)

We provide a pre-configured Grafana Dashboard that visualizes the health of your API in real-time.

**Tracks:**
*   **SLO Tracking**: Error Budget Burn Rate (Are we reliable enough?)
*   **User Experience**: P99 Latency (How slow is the slowest 1%?)
*   **Resilience**: Live Circuit Breaker status.

**How to Import:**
1.  Open Grafana (`http://localhost:3030`).
2.  Go to **Dashboards** -> **New** -> **Import**.
3.  Upload the file: `infra/grafana/dashboard.json`.
4.  Select **Prometheus** as the data source.

![Grafana Dashboard](grafana-dashboard.png)

## 2. Distributed Tracing (Jaeger)

Every request is traced using OpenTelemetry.

### Incoming Traces
When a client hits `GET /health`, the app starts a trace. Middleware adds:
- `trace_id`: Global unique identifier.
- `span_id`: Identifier for this specific operation.
- `correlation_id`: A user-facing ID for support tickets.

### Outgoing Propagation
We use an **Instrumented HTTP Client** (`src/infrastructure/http_client.py`). When your API calls an external service (like OpenAI or Stripe), it automatically injects:
- `traceparent` header (W3C standard).
- `X-Correlation-ID` header.

This ensures you don't lose visibility when traffic leaves your network.

## 3. Resilience Patterns

### Circuit Breaker
Located in `src/core/circuit_breaker.py`.
- **Logic**: If an external service fails 5 times in a row, the breaker "trips" (Open state).
- **Protection**: Subsequent requests fail immediately (Fail Fast) or return cached data.
- **Recovery**: After a cooldown (60s), it lets one request through (Half-Open) to check if the service is back.

### Rate Limiting
Located in `src/core/rate_limit.py`.
- Implements the **Token Bucket** algorithm.
- Protects endpoints like `/login` from brute-force attacks.
