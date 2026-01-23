# Performance Guide

The API Reliability Suite is engineered for high-performance, utilizing modern asynchronous patterns and observability-driven optimization.

---

## ⚡ Application Performance

### Asynchronous Execution
The entire API (FastAPI) and its core features (LLM analysis, logging, file I/O) use non-blocking **async/await**. This allows the server to handle thousands of concurrent requests without thread starvation.

**Key async components:**
- **`src/main.py`**: All routes and lifespan events.
- **`src/core/llm.py`**: Asynchronous calls to LLM providers.
- **`src/core/logging.py`**: Asynchronous log processing with structlog.

### Circuit Breaker (Fault Tolerance)
We use `pybreaker` to prevent slow downstream dependencies from degrading system performance. By "tripping" the circuit after repeated failures, we avoid long timeouts and preserve resource headroom for healthy requests.

---

## 📊 Performance Monitoring

### The "Golden Signals"
We monitor the four golden signals via the integrated **Prometheus-FastAPI-Instrumentator**:

1.  **Latency:** Time taken to service a request (split by endpoint).
2.  **Traffic:** Demand placed on the system (Requests Per Second).
3.  **Errors:** Rate of requests that fail (5xx errors).
4.  **Saturation:** Resource utilization (CPU/Memory via Kubernetes HPA metrics).

### Distributed Tracing
OpenTelemetry is used to identify performance bottlenecks. By examining traces in **Jaeger**, you can see exactly how much time is spent in:
- Middleware processing.
- Service layer logic.
- External API calls.

---

## 🚀 Optimization Checklist

### Development Tuning
- [ ] **Log Level:** Set `LOG_LEVEL=warning` in performance tests to reduce I/O overhead.
- [ ] **OTLP Endpoint:** Disable tracing (`OTLP_ENDPOINT=""`) if you only need to benchmark raw throughput.

### Production Tuning
- [ ] **Workers:** Increase the number of Uvicorn workers (e.g., `workers = (2 * CPU) + 1`).
- [ ] **Kubernetes HPA:** Adjust the CPU target in `infra/k8s/hpa.yaml` based on your specific load profile.
