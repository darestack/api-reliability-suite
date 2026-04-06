# Load Testing

This page documents the smoke-load profile for the API Reliability Suite and the latest local baseline captured from a real run.

---

## Smoke Profile

The k6 smoke script lives in `loadtests/k6/reliability-smoke.js`.

It uses one login during `setup()` and then exercises three representative paths:

- `/protected` as the authenticated fast path
- `/external-api` as the resilience path behind the circuit breaker
- `/slow` as the bounded latency probe

The traffic profile is intentionally sized to stay within the app's route-level rate limits, so this is a smoke benchmark, not a capacity benchmark.

## Run It

The simplest path uses the Make target, which stamps the current Git SHA and test date into the generated report:

```bash
make load-test
```

Equivalent direct command:

```bash
k6 run \
  -e BASE_URL=http://localhost:8000 \
  -e ENV_NAME=local-docker-compose \
  -e GIT_SHA=$(git rev-parse --short HEAD)$(git diff --quiet --ignore-submodules HEAD -- || printf -- '-dirty') \
  -e TEST_DATE=$(date -u +%F) \
  loadtests/k6/reliability-smoke.js
```

If the API is running in Docker Compose, `BASE_URL=http://localhost:8000` works from the host shell. For another target, override `BASE_URL`, `LOAD_TEST_USERNAME`, and `LOAD_TEST_PASSWORD`.

---

## Generated Artifacts

The script writes:

- `loadtests/results/latest-report.md`
- `loadtests/results/latest-summary.json`

These are overwritten on each run so the latest local smoke snapshot is always easy to inspect.

## Latest Local Smoke Snapshot

This section is updated from a real run against the local Docker Compose stack and should be treated as a local baseline, not a portability guarantee.

- Date: `2026-04-06`
- Environment: `local-docker-compose` with host-port overrides for Postgres (`15432`) and Redis (`16379`)
- Commit: `ab3d869-dirty`
- Command: `make load-test`

### Thresholds

- `/protected` error rate: < 1%
- `/protected` p95 latency: < 500 ms
- `/external-api` error rate: < 1%
- `/external-api` p95 latency: < 500 ms
- `/slow` error rate: < 1%
- `/slow` p95 latency: < 2500 ms

### Observed Results

- Aggregate request rate: `0.94 req/s`
- `/protected` error rate: `0.00%`
- `/protected` p95 latency: `8.86 ms`
- `/external-api` error rate: `0.00%`
- `/external-api` p95 latency: `5.84 ms`
- `/slow` error rate: `0.00%`
- `/slow` p95 latency: `2009.37 ms`

### Follow-Up Checks

- After the next Prometheus recording-rule evaluation, `/slo/report` reported:
  - `request_rate_5m`: about `0.56 req/s`
  - `error_ratio_5m`: `0.0`
  - `p99_latency_seconds_5m`: `1.0`
  - `error_budget_burn_rate_5m`: `0.0`
- Prometheus evaluates the bundled recording rules every `60` seconds, so a fresh smoke run may take one evaluation cycle before the recorded series catches up.
- Review the `API Reliability SLO Overview` Grafana dashboard at `http://localhost:3030/d/api-reliability-slo`.
- Check Alertmanager at `http://localhost:9093` if thresholds were crossed.

## SLO View

The Prometheus recording rules expose SLO-friendly series such as:

- `api:http_requests:error_ratio_5m`
- `api:http_request_duration_seconds:p99_5m`
- `api:error_budget_burn_rate_5m`

Use those values when you summarize load-test impact in docs or incident notes.
