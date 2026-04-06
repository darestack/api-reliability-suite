# Load Testing

This page provides the load-test scaffold for the API Reliability Suite and a simple report template for sharing results.

---

## Test Script

The current k6 scaffold lives in `loadtests/k6/reliability-smoke.js`.

It exercises:
- `/health` for a fast smoke path
- `/slow` for a bounded latency probe

The script uses per-endpoint tags and thresholds so health checks and latency probes can be measured separately.

### Run It

If you have k6 installed locally:

```bash
k6 run loadtests/k6/reliability-smoke.js
```

If you prefer the official container image:

```bash
docker run --rm -i -e BASE_URL=http://localhost:8000 grafana/k6:latest run - < loadtests/k6/reliability-smoke.js
```

Adjust `BASE_URL` for your environment if the API is not on `localhost:8000`. If you are using the Docker compose stack, `localhost:8000` works from the host shell.

---

## What To Capture

Record the following after each run:

- test date and environment
- script version or commit SHA
- command used
- response failure rate
- p95 latency for `/health`
- p95 latency for `/slow`
- any alert noise or breaker state changes

---

## Report Template

```markdown
# Load Test Report

- Date:
- Environment:
- Commit:
- Command:

## Target Thresholds

- `/health` error rate: < 1%
- `/health` p95 latency: < 500 ms
- `/slow` p95 latency: < 2500 ms

## Observed Results

- `/health` error rate:
- `/health` p95 latency:
- `/slow` p95 latency:
- Alertmanager activity:
- Grafana observations:

## Notes

- What changed in the stack:
- What should be tuned next:
```

---

## SLO View

The Prometheus recording rules expose SLO-friendly series such as:

- `api:http_requests:error_ratio_5m`
- `api:http_request_duration_seconds:p99_5m`
- `api:error_budget_burn_rate_5m`

Use those values when you summarize load-test impact in docs or incident notes.
