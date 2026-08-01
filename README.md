# LearnOps

A small student-learning-events pipeline used as the payload for a real
DevOps/platform-engineering exercise: Terraform-provisioned Kubernetes,
GitOps delivery via ArgoCD, a CI/CD pipeline that actually builds/scans/
promotes images, and full observability with Prometheus, Grafana, and
alerting.

The app itself is intentionally simple - an API that ingests learning
events and a worker that aggregates them into per-student progress. The
interesting part is everything around it. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full picture and
[`docs/DEMO.md`](docs/DEMO.md) for a live walkthrough script. A separate
platform-engineering proposal (not part of this repo) uses this project as
its working evidence.

## Stack

- **App**: Python / FastAPI (`apps/ingest-api`), a Redis-backed worker
  (`apps/aggregator-worker`), Postgres for durable progress storage. Both
  services expose `/healthz` (ingest-api only), `/readyz` (ingest-api only),
  and Prometheus `/metrics`.
- **CI/CD**: GitHub Actions - lint (hadolint, kubeconform) -> test (against
  real Postgres/Redis service containers, not mocks) -> build -> Trivy scan
  -> push to GHCR -> bump the production image tag in git.
- **IaC**: Terraform (`infra/terraform/local`) provisions a local `kind`
  cluster and bootstraps ArgoCD + kube-prometheus-stack. A separate,
  never-applied `infra/terraform/gcp-reference` module shows the same
  platform mapped onto real GCP infrastructure (GKE Autopilot, Cloud SQL,
  Memorystore).
- **GitOps**: ArgoCD watches `k8s/overlays/production` and auto-syncs -
  Terraform never deploys the app directly.
- **Manifests**: Kustomize, `k8s/base` + `overlays/staging` +
  `overlays/production`.
- **Observability**: ServiceMonitors, a provisioned Grafana dashboard, and a
  PrometheusRule with real alerts (see
  [`docs/RUNBOOK.md`](docs/RUNBOOK.md)).

## Quickstart (fast local loop)

Requires Docker Desktop.

```bash
docker compose up -d --build ```

| What | URL |
|---|---|
| ingest-api | http://localhost:8001 |

```bash
curl -X POST http://localhost:8001/events \
  -H "Content-Type: application/json" \
  -d '{"student_id":"s1","lesson_id":"l1","event_type":"lesson_completed","score":92}'

curl http://localhost:8001/progress/s1
```

## Quickstart (full platform - Kubernetes, ArgoCD, observability)

Requires Docker Desktop, `kind`, `kubectl`, `helm`, and `terraform`.

```bash
cd infra/terraform/local
terraform init
terraform apply
```

This creates a 3-node `kind` cluster and installs ArgoCD and
kube-prometheus-stack. First run takes several minutes (Helm chart image
pulls). Once it settles, build and load the app images (until this repo is
pushed to GitHub and CI publishes them to GHCR):

```bash
cd ../../..
docker build -t ghcr.io/bims-creator/learnops-ingest-api:latest ./apps/ingest-api
docker build -t ghcr.io/bims-creator/learnops-aggregator-worker:latest ./apps/aggregator-worker
kind load docker-image ghcr.io/bims-creator/learnops-ingest-api:latest --name learnops
kind load docker-image ghcr.io/bims-creator/learnops-aggregator-worker:latest --name learnops
kubectl --kubeconfig infra/terraform/local/.kubeconfig apply -k k8s/overlays/production
```

| What | URL | Credentials |
|---|---|---|
| App | http://localhost:31080 | - |
| Grafana | http://localhost:31030 | `admin` / value of `grafana_admin_password` var |
| Prometheus | http://localhost:31090 | - |
| ArgoCD | `kubectl --kubeconfig infra/terraform/local/.kubeconfig -n argocd port-forward svc/argocd-server 8080:80`, then http://localhost:8080 | `admin` / `kubectl --kubeconfig infra/terraform/local/.kubeconfig -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' \| base64 -d` |

## Tear down

```bash
cd infra/terraform/local
terraform destroy
```

## Repo layout

```
apps/                     ingest-api + aggregator-worker source, tests, Dockerfiles
infra/terraform/local/    kind cluster + ArgoCD + kube-prometheus-stack bootstrap
infra/terraform/gcp-reference/  real GCP Terraform - documentation only, never applied
k8s/base/                 Kustomize base manifests (Deployments, HPA, ServiceMonitors,
                          PrometheusRule, Grafana dashboard ConfigMap)
k8s/overlays/             staging + production environment overlays
.github/workflows/        CI/CD pipeline
docs/                     architecture, runbook, demo script, platform proposal
```