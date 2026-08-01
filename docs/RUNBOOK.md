# Runbook

## Accessing the platform

| Tool | How | Credentials |
|---|---|---|
| App (ingest-api) | http://localhost:31080 (kind) or http://localhost:8001 (docker compose) | - |
| Grafana | http://localhost:31030 | `admin` / `grafana_admin_password` Terraform variable (default `learnops-demo`) |
| Prometheus | http://localhost:31090 | - |
| ArgoCD | `kubectl --kubeconfig infra/terraform/local/.kubeconfig -n argocd port-forward svc/argocd-server 8080:80`, then http://localhost:8080 | `admin` / `kubectl --kubeconfig infra/terraform/local/.kubeconfig -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' \| base64 -d` |

## Alerts

### ServiceDown
`up{job=~"ingest-api|aggregator-worker"} == 0` for 2 minutes.

**Response:** `kubectl -n learnops get pods`, then `kubectl -n learnops logs <pod>`
for the crashing service. A few restarts right after Postgres itself
restarts is expected and self-heals (see ARCHITECTURE.md's note on
`ingest-api`'s eager Postgres connection); sustained downtime is not.

### HighEventFailureRate
`rate(learnops_events_failed_total[5m]) > 0` for 5 minutes.

**Response:** `kubectl -n learnops logs -l app.kubernetes.io/name=aggregator-worker` -
the worker logs the full exception via `log.exception(...)` on every failed
event, so the cause is directly in the logs, not just the metric.

### IngestApiAutoscalerMaxedOut
`ingest-api`'s HPA has been at `maxReplicas` (6) for 10+ minutes.

**Response:** Check whether this is real sustained load
(`kubectl -n learnops top pods`) vs a runaway client. If real, raise
`maxReplicas` in `k8s/base/ingest-api.yaml`, or check whether requests are
actually Postgres-bound rather than CPU-bound, in which case adding API
replicas won't help.

## Troubleshooting (things we actually hit building this)

### Helm release stuck in `pending-install` after an interrupted apply
If `terraform apply` gets interrupted (network blip, machine sleep)
mid-Helm-install, the release can be left in `pending-install` or `failed`
state, and a retry fails with "cannot re-use a name that is still in use":

```bash
helm --kubeconfig infra/terraform/local/.kubeconfig list -A
helm --kubeconfig infra/terraform/local/.kubeconfig uninstall <release> -n <namespace>
terraform apply
```

### Control-plane pods crash-looping (scheduler, controller-manager, metrics-server)
If you're running more than one `kind` cluster at once, they compete for
host CPU hard enough to starve the control plane's own leader-election
lease renewals, cascading into scheduler/controller-manager
`CrashLoopBackOff`, which then blocks anything new from being scheduled at
all. Diagnose with:

```bash
docker stats --no-stream
```

If CPU is pinned near 100%+ across multiple `kind`-node containers, delete
the cluster(s) you don't need right now
(`kind delete cluster --name <other-cluster>`), then force a clean restart
of the still-wedged control-plane pods (static pods need the pod object
deleted directly, not the deployment):

```bash
kubectl --kubeconfig infra/terraform/local/.kubeconfig -n kube-system delete pod kube-scheduler-learnops-control-plane
kubectl --kubeconfig infra/terraform/local/.kubeconfig -n kube-system delete pod kube-controller-manager-learnops-control-plane
```

### `TLS handshake timeout` connecting to the kind API server
Usually means Docker Desktop's VM lost its network tunnel after the machine
slept/suspended, even though `docker ps` still shows the containers as
`Up`. Restart Docker Desktop entirely (quit from the tray icon, relaunch,
wait for "Engine running"), then retry `kubectl get nodes`.

### A local port that should be free returns a response from the wrong process
On Windows, `netstat -ano` can show a `LISTENING` PID for a port that
`tasklist` reports doesn't exist - check with
`tasklist //FI "PID eq <pid>"` first; if it comes back empty, that listener
is a ghost. When in doubt, just move to a different local port rather than
debugging the ghost further.