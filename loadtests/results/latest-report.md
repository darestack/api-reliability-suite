# Load Test Report

- Date: 2026-04-06
- Environment: local-docker-compose
- Commit: ab3d869-dirty
- Command: k6 run loadtests/k6/reliability-smoke.js

## Target Thresholds

- `/protected` error rate: < 1%
- `/protected` p95 latency: < 500 ms
- `/external-api` error rate: < 1%
- `/external-api` p95 latency: < 500 ms
- `/slow` error rate: < 1%
- `/slow` p95 latency: < 2500 ms

## Observed Results

- Aggregate request rate: 0.94 req/s
- `/protected` error rate: 0.00%
- `/protected` p95 latency: 8.86 ms
- `/external-api` error rate: 0.00%
- `/external-api` p95 latency: 5.84 ms
- `/slow` error rate: 0.00%
- `/slow` p95 latency: 2009.37 ms

## Notes

- This smoke profile is intentionally sized to stay within the API's route-level rate limits.
- Treat these results as a local baseline, not a portability guarantee across hosts or deployment targets.
