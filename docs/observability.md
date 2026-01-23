# Monitoring & Metrics

This suite provides enterprise-grade observability out of the box using the **Prometheus**, **Grafana**, and **Jaeger** stack.

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

Every request is traced using **OpenTelemetry**, providing visibility into how requests flow through your system.

### Trace Propagation
- **Inbound**: Middleware automatically injects `trace_id`, `span_id`, and a user-facing `correlation_id`.
- **Outbound**: The instrumented HTTP client (`src/infrastructure/http_client.py`) propagates context to external services (like Groq or OpenAI) via **W3C `traceparent`** headers.

!!! info "Dashboard Access"
    View live traces at [http://localhost:16686](http://localhost:16686).

---

## 🚨 Alerting Strategy

Prometheus is configured with **Golden Signal** alerts to proactively notify you of system distress.

| Alert | Condition | Severity |
| :--- | :--- | :--- |
| **HighErrorRate** | 5xx Errors > 5% | Critical |
| **HighLatency** | P99 Latency > 1s | Warning |
| **CircuitBreakerOpen** | Breaker state is "Open" | Warning |

!!! example "Alert Config"
    Rules are defined in `infra/prometheus/alert_rules.yml`.
