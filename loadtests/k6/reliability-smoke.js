import http from 'k6/http';
import { check } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const LOAD_TEST_USERNAME = __ENV.LOAD_TEST_USERNAME || 'demo';
const LOAD_TEST_PASSWORD = __ENV.LOAD_TEST_PASSWORD || 'secret123';
const ENV_NAME = __ENV.ENV_NAME || 'local';
const GIT_SHA = __ENV.GIT_SHA || 'unknown';
const TEST_DATE = __ENV.TEST_DATE || new Date().toISOString().slice(0, 10);

const protectedLatency = new Trend('protected_latency', true);
const externalApiLatency = new Trend('external_api_latency', true);
const slowLatency = new Trend('slow_latency', true);

const protectedFailures = new Rate('protected_failures');
const externalApiFailures = new Rate('external_api_failures');
const slowFailures = new Rate('slow_failures');

export const options = {
  scenarios: {
    authenticated_protected: {
      executor: 'constant-arrival-rate',
      rate: 30,
      timeUnit: '1m',
      duration: '1m',
      preAllocatedVUs: 4,
      maxVUs: 8,
      exec: 'protectedRead',
    },
    external_dependency: {
      executor: 'constant-arrival-rate',
      rate: 20,
      timeUnit: '1m',
      duration: '1m',
      preAllocatedVUs: 4,
      maxVUs: 8,
      exec: 'externalApiRead',
    },
    slow_probe: {
      executor: 'constant-arrival-rate',
      rate: 5,
      timeUnit: '1m',
      duration: '1m',
      preAllocatedVUs: 2,
      maxVUs: 4,
      exec: 'slowProbe',
    },
  },
  thresholds: {
    protected_failures: ['rate<0.01'],
    protected_latency: ['p(95)<500'],
    external_api_failures: ['rate<0.01'],
    external_api_latency: ['p(95)<500'],
    slow_failures: ['rate<0.01'],
    slow_latency: ['p(95)<2500'],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)'],
};

export function setup() {
  const loginPayload = `username=${encodeURIComponent(LOAD_TEST_USERNAME)}&password=${encodeURIComponent(LOAD_TEST_PASSWORD)}`;
  const loginResponse = http.post(
    `${BASE_URL}/login`,
    loginPayload,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      tags: { endpoint: 'login' },
    }
  );

  check(loginResponse, {
    'login responds with 200': (res) => res.status === 200,
  });

  if (loginResponse.status !== 200) {
    throw new Error(`Load-test setup failed: login returned ${loginResponse.status}`);
  }

  return { token: loginResponse.json('access_token') };
}

export function protectedRead(data) {
  const response = http.get(`${BASE_URL}/protected`, {
    headers: { Authorization: `Bearer ${data.token}` },
    tags: { endpoint: 'protected' },
  });

  protectedLatency.add(response.timings.duration);
  protectedFailures.add(response.status !== 200);

  check(response, {
    'protected responds with 200': (res) => res.status === 200,
  });
}

export function externalApiRead() {
  const response = http.get(`${BASE_URL}/external-api`, {
    tags: { endpoint: 'external-api' },
  });

  externalApiLatency.add(response.timings.duration);
  externalApiFailures.add(response.status !== 200);

  check(response, {
    'external-api responds with 200': (res) => res.status === 200,
  });
}

export function slowProbe() {
  const response = http.get(`${BASE_URL}/slow`, {
    tags: { endpoint: 'slow' },
  });

  slowLatency.add(response.timings.duration);
  slowFailures.add(response.status !== 200);

  check(response, {
    'slow endpoint responds with 200': (res) => res.status === 200,
  });
}

function metricValue(data, name, key) {
  const metric = data.metrics[name];
  if (!metric || !metric.values) {
    return null;
  }

  return metric.values[key] ?? null;
}

function formatPercent(value) {
  if (value === null) {
    return 'n/a';
  }

  return `${(value * 100).toFixed(2)}%`;
}

function formatMs(millisecondsValue) {
  if (millisecondsValue === null) {
    return 'n/a';
  }

  return `${millisecondsValue.toFixed(2)} ms`;
}

function formatRate(value) {
  if (value === null) {
    return 'n/a';
  }

  return `${value.toFixed(2)} req/s`;
}

export function handleSummary(data) {
  const protectedFailureRate = metricValue(data, 'protected_failures', 'rate');
  const protectedP95 = metricValue(data, 'protected_latency', 'p(95)');
  const externalFailureRate = metricValue(data, 'external_api_failures', 'rate');
  const externalP95 = metricValue(data, 'external_api_latency', 'p(95)');
  const slowFailureRate = metricValue(data, 'slow_failures', 'rate');
  const slowP95 = metricValue(data, 'slow_latency', 'p(95)');
  const requestRate = metricValue(data, 'http_reqs', 'rate');

  const markdownReport = `# Load Test Report

- Date: ${TEST_DATE}
- Environment: ${ENV_NAME}
- Commit: ${GIT_SHA}
- Command: k6 run loadtests/k6/reliability-smoke.js

## Target Thresholds

- \`/protected\` error rate: < 1%
- \`/protected\` p95 latency: < 500 ms
- \`/external-api\` error rate: < 1%
- \`/external-api\` p95 latency: < 500 ms
- \`/slow\` error rate: < 1%
- \`/slow\` p95 latency: < 2500 ms

## Observed Results

- Aggregate request rate: ${formatRate(requestRate)}
- \`/protected\` error rate: ${formatPercent(protectedFailureRate)}
- \`/protected\` p95 latency: ${formatMs(protectedP95)}
- \`/external-api\` error rate: ${formatPercent(externalFailureRate)}
- \`/external-api\` p95 latency: ${formatMs(externalP95)}
- \`/slow\` error rate: ${formatPercent(slowFailureRate)}
- \`/slow\` p95 latency: ${formatMs(slowP95)}

## Notes

- This smoke profile is intentionally sized to stay within the API's route-level rate limits.
- Treat these results as a local baseline, not a portability guarantee across hosts or deployment targets.
`;

  return {
    stdout: `${markdownReport}\n`,
    'loadtests/results/latest-report.md': markdownReport,
    'loadtests/results/latest-summary.json': JSON.stringify(data, null, 2),
  };
}
