import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  scenarios: {
    health_smoke: {
      executor: 'constant-vus',
      vus: 5,
      duration: '1m',
      exec: 'healthSmoke',
    },
    latency_probe: {
      executor: 'constant-vus',
      vus: 2,
      duration: '45s',
      exec: 'latencyProbe',
    },
  },
  thresholds: {
    'http_req_failed{endpoint:health}': ['rate<0.01'],
    'http_req_duration{endpoint:health}': ['p(95)<500'],
    'http_req_duration{endpoint:slow}': ['p(95)<2500'],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)'],
};

export function healthSmoke() {
  const response = http.get(`${BASE_URL}/health`, {
    tags: { endpoint: 'health' },
  });

  check(response, {
    'health responds with 200': (res) => res.status === 200,
  });

  sleep(1);
}

export function latencyProbe() {
  const response = http.get(`${BASE_URL}/slow`, {
    tags: { endpoint: 'slow' },
  });

  check(response, {
    'slow endpoint responds with 200': (res) => res.status === 200,
  });

  sleep(1);
}
