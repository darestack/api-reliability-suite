# Monitoring & Metrics

This suite includes a practical observability starter stack built around **Prometheus**, **Grafana**, and **Jaeger**.

---

## 📊 Real-Time Dashboard (Grafana)

The suite includes a comprehensive Grafana Dashboard designed for SREs and Reliability Engineers.

![Grafana Dashboard](assets/grafana-dashboard.png)

### Key Metrics Tracked
- **SLO Tracking**: Monitors the Error Budget Burn Rate to detect reliability risks early.
- **Latency Distribution**: Tracks P99 Latency to ensure performance for tail-end users.
- **System Resilience**: Visualizes Circuit Breaker states in real-time.

!!! tip "Import Instructions"
    1.  Access Grafana at `http://localhost:3030`.
    2.  Navigate to **Dashboards** &rarr; **New** &rarr; **Import**.
    3.  Upload the configuration file: `infra/grafana/dashboard.json`.
    4.  Select **Prometheus** as the data source.

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

The local Prometheus container loads **Golden Signal** alert rules so you can inspect firing conditions during demos and manual testing.

| Alert | Condition | Severity |
| :--- | :--- | :--- |
| **HighErrorRate** | 5xx Errors > 5% | Critical |
| **HighLatency** | P99 Latency > 1s | Warning |
| **CircuitBreakerOpen** | Breaker state is "Open" | Warning |

!!! example "Alert Config"
    Rules are defined in `infra/prometheus/alert_rules.yml` and mounted into the local Prometheus container at `/etc/prometheus/alert_rules.yml`.
