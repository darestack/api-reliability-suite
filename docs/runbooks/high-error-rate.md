# Incident Runbook: High Error Rate

Use this runbook when the `HighErrorRate` alert fires.

---

## Alert Context

- Alert name: `HighErrorRate`
- Source: Prometheus rule in `infra/prometheus/alert_rules.yml`
- Default threshold: 5xx error ratio above 5% for 1 minute

---

## Immediate Checks

1. Open Alertmanager at `http://localhost:9093` and confirm the alert is firing.
2. Open Prometheus at `http://localhost:9099/targets` and confirm the `fastapi` scrape target is `UP`.
3. Check the recorded SLO series in Prometheus:
   - `api:http_requests:error_ratio_5m`
   - `api:error_budget_burn_rate_5m`
4. Inspect recent API logs with `make debug` or by reading the configured `LOG_FILE_PATH`.

---

## Triage Questions

- Did a recent deploy change the error rate?
- Is the circuit breaker open because an upstream dependency is failing?
- Are the errors limited to one endpoint or one user flow?
- Is Redis healthy if rate limiting or fallback caching depends on it?

---

## Mitigation Steps

- Roll back the last deploy if the errors started immediately after release.
- Reduce traffic if the service is saturating.
- Silence the alert only after the failure mode is understood.
- Preserve logs, alert timestamps, and Grafana screenshots for the incident record.

---

## After Action

- Update `docs/load-testing.md` or attach a new dated smoke-test report if the incident changed the local baseline.
- Capture the fix, the detection gap, and the follow-up action.
- If the alert was noisy or incomplete, update the Prometheus rule or dashboard note.
