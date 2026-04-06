# Monitoring & Metrics

This suite includes a practical observability starter stack built around **Prometheus**, **Grafana**, and **Jaeger**.

The app also exposes a dependency-aware `/ready` endpoint so operators can distinguish between basic process health and backing-service readiness.

---

## 📊 Real-Time Dashboard (Grafana)

The Docker Compose stack provisions the Prometheus data source and the `API Reliability SLO Overview` dashboard automatically.

### Key Metrics Tracked
- **SLO Tracking**: Success ratio, p99 latency, request rate, and error-budget burn rate.
- **Latency Distribution**: Tracks the 5-minute p99 latency recording rule for tail behavior.
- **System Resilience**: Visualizes the circuit breaker state in real time.

!!! tip "Open the Provisioned Dashboard"
    1.  Start the stack with `make stack-up`.
    2.  Access Grafana at `http://localhost:3030` with `admin / admin`.
    3.  Open `http://localhost:3030/d/api-reliability-slo`.

Provisioning files live in:

- `infra/grafana/provisioning/datasources/prometheus.yml`
- `infra/grafana/provisioning/dashboards/dashboards.yml`
- `infra/grafana/dashboards/api-reliability-overview.json`

---

## 🔗 Distributed Tracing (Jaeger)

Requests can be traced using **OpenTelemetry**, providing visibility into how traffic moves through the application during local runs and demos.

### Trace Propagation
- **Inbound**: Middleware automatically injects `trace_id`, `span_id`, and a user-facing `correlation_id`.
- **Outbound**: The instrumented HTTP client (`src/infrastructure/http_client.py`) propagates context to external services (like Groq or OpenAI) via **W3C `traceparent`** headers.

!!! info "Dashboard Access"
    View live traces at [http://localhost:16686](http://localhost:16686).

---

## 🚨 Alerting Strategy

The local Prometheus container loads **Golden Signal** alert rules and forwards them to Alertmanager so you can inspect firing conditions during demos and manual testing.

| Alert | Condition | Severity |
| :--- | :--- | :--- |
| **HighErrorRate** | 5xx Errors > 5% | Critical |
| **HighLatency** | P99 Latency > 1s | Warning |
| **CircuitBreakerOpen** | Breaker state is "Open" | Warning |

!!! example "Alert Config"
    Rules are defined in `infra/prometheus/alert_rules.yml`, mounted into the local Prometheus container at `/etc/prometheus/alert_rules.yml`, and routed to Alertmanager at `http://localhost:9093`.

!!! info "Recording Rules"
    Prometheus also records SLO-oriented series for request rate, error ratio, p99 latency, and error-budget burn rate. See [`docs/load-testing.md`](load-testing.md) for the smoke profile and the latest recorded local baseline.
