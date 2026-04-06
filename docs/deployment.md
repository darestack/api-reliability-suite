# Deployment Guide

The API Reliability Suite is designed to be cloud-native and highly portable, utilizing Docker for containerization and Kubernetes for orchestration.

---

## 🐳 Containerization

### Dockerfile

The project uses a **multi-stage Docker build** to minimize the final image size and reduce the attack surface.

- **Stage 1 (Builder):** Installs Poetry and downloads all runtime dependencies.
- **Stage 2 (Runtime):** Copies the installed packages, the `src/` application code, and the runtime helper scripts into a pinned Python 3.12 slim image.
- **Runtime User:** The container drops root and runs as the dedicated `app` user (`UID/GID 10001`).

### Building the Image
```bash
make docker-build
```

> [!NOTE]
> The local `docker-compose.yml` stack includes Postgres for user persistence, Redis for rate limiting and breaker fallback caching, Prometheus, Alertmanager, Jaeger, and Grafana. Production deployments should configure equivalent shared services through environment variables and secrets.

---

## ☸️ Kubernetes (Infrastructure as Code)

Example manifests are located in `infra/k8s/` to show a baseline deployment layout and scaling strategy.

### 1. Deployment (`deployment.yaml`)
The deployment ensures at least **2 replicas** are always running.

- **Probes:** `livenessProbe` uses `/health`, while `readinessProbe` uses `/ready` so traffic is only sent to pods whose database and shared dependencies are reachable.
- **Resources:** Sets explicit CPU and Memory requests/limits to prevent resource contention.
- **Metrics:** Annotated for automatic Prometheus scraping.
- **Security Context:** Runs as a non-root user, drops Linux capabilities, and uses the runtime-default seccomp profile.
- **Rollout Strategy:** Uses a rolling update strategy with `revisionHistoryLimit` so rollbacks stay available.

### 2. Auto-scaling (`hpa.yaml`)
A `HorizontalPodAutoscaler` is configured to scale the API based on CPU utilization.

- **Min/Max:** Scales between 2 and 10 pods.
- **Target:** Triggers scaling when average CPU utilization hits 70%.
- **Stability:** Includes a `stabilizationWindowSeconds` of 300 to prevent "flapping" (rapid scaling up and down during minor load fluctuations).

### Applying to Cluster
```bash
kubectl apply -f infra/k8s/
```

> [!NOTE]
> The templates expect secrets to be injected through Kubernetes Secrets (see `infra/k8s/deployment.yaml`), and shared environments should provide `DATABASE_URL`, `RATE_LIMIT_STORAGE_URI`, and `CIRCUIT_BREAKER_CACHE_URL`.

### Release and Rollback Discipline

For shared environments, avoid mutable image tags such as `latest`.

Recommended release flow:

1. Build and push a versioned image tag such as `ghcr.io/daretechie/api-reliability-suite:1.2.0`.
2. Update `infra/k8s/deployment.yaml` to that immutable release tag.
3. Apply the manifest and watch rollout health with `kubectl rollout status deployment/reliability-api`.
4. If the rollout is unhealthy, use `kubectl rollout undo deployment/reliability-api`.

### Backups and Restore Notes

Once Postgres is your primary identity store, backup and restore need to be part of the deploy plan.

- Capture logical backups with `pg_dump -Fc`.
- Test restores with `pg_restore` into a fresh database before calling a backup policy complete.
- Run `poetry run alembic upgrade head` during deployment so schema state stays aligned with application code.

---

## 📊 Observability Stack

When deploying to a cluster, ensure the following services are available (or use the provided `docker-compose.yml` for local testing):

- **Prometheus:** Scrapes metrics from the `/metrics` endpoint.
- **Alertmanager:** Receives Prometheus alerts and keeps alert routing close to the metrics stack.
- **Jaeger:** Receives distributed traces via the OTLP exporter (if `OTLP_ENDPOINT` is configured).
- **Grafana:** Visualizes the "Golden Signals" (Latency, Errors, Traffic, Saturation).

---

## 🚀 CI/CD Integration

The provided Docker and K8s assets are designed to integrate seamlessly with CI/CD runners (GitHub Actions, GitLab CI).

1.  **Build:** Create the image using the multi-stage Dockerfile.
2.  **Push:** Push the image to your private registry (ECR, GCR, ACR).
3.  **Deploy:** Update the `image` field in `infra/k8s/deployment.yaml` and apply.
