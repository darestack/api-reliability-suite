# Deployment Guide

The API Reliability Suite is designed to be cloud-native and highly portable, utilizing Docker for containerization and Kubernetes for orchestration.

---

## 🐳 Containerization

### Dockerfile

The project uses a **multi-stage Docker build** to minimize the final image size and reduce the attack surface.

- **Stage 1 (Builder):** Installs Poetry and downloads all dependencies.
- **Stage 2 (Runtime):** Copies only the installed packages and the `src/` directory into a slim Python 3.12 image.

### Building the Image
```bash
make docker-build
```

---

## ☸️ Kubernetes (Infrastructure as Code)

Production-ready manifests are located in `infra/k8s/`. These manifests follow the 2026 Reliability Standards for high-availability APIs.

### 1. Deployment (`deployment.yaml`)
The deployment ensures at least **2 replicas** are always running.

- **Probes:** Includes both `livenessProbe` and `readinessProbe` pointing to the `/health` endpoint to ensure the cluster only sends traffic to healthy pods.
- **Resources:** Sets explicit CPU and Memory requests/limits to prevent resource contention.
- **Metrics:** Annotated for automatic Prometheus scraping.

### 2. Auto-scaling (`hpa.yaml`)
A `HorizontalPodAutoscaler` is configured to scale the API based on CPU utilization.

- **Min/Max:** Scales between 2 and 10 pods.
- **Target:** Triggers scaling when average CPU utilization hits 70%.
- **Stability:** Includes a `stabilizationWindowSeconds` of 300 to prevent "flapping" (rapid scaling up and down during minor load fluctuations).

### Applying to Cluster
```bash
kubectl apply -f infra/k8s/
```

---

## 📊 Observability Stack

When deploying to a cluster, ensure the following services are available (or use the provided `docker-compose.yml` for local testing):

- **Prometheus:** Scrapes metrics from the `/metrics` endpoint.
- **Jaeger:** Receives distributed traces via the OTLP exporter (if `OTLP_ENDPOINT` is configured).
- **Grafana:** Visualizes the "Golden Signals" (Latency, Errors, Traffic, Saturation).

---

## 🚀 CI/CD Integration

The provided Docker and K8s assets are designed to integrate seamlessly with CI/CD runners (GitHub Actions, GitLab CI).

1.  **Build:** Create the image using the multi-stage Dockerfile.
2.  **Push:** Push the image to your private registry (ECR, GCR, ACR).
3.  **Deploy:** Update the `image` field in `infra/k8s/deployment.yaml` and apply.
