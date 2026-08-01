# Demo script

A live walkthrough for showing this repo end-to-end (~10 minutes).

## 1. Fast local loop (2 min)

```bash
docker compose up -d --build
curl -X POST http://localhost:8001/events \
  -H "Content-Type: application/json" \
  -d '{"student_id":"demo","lesson_id":"l1","event_type":"lesson_completed","score":91}'
curl http://localhost:8001/progress/demo
```

Talking point: this replaces the brief's "2 days to onboard" pain point
with two commands.

## 2. The full platform (3 min)

Assuming `terraform apply` has already been run ahead of time (it takes
several minutes, so don't do this live):

```bash
kubectl --kubeconfig infra/terraform/local/.kubeconfig get pods -n learnops
curl http://localhost:31080/healthz
```

Open Grafana (http://localhost:31030, `admin` / password) and show the
LearnOps dashboard - events ingested/processed/failed rates, live.

## 3. Observability (2 min)

Open Prometheus (http://localhost:31090/targets) - show `ingest-api` and
`aggregator-worker` both `UP`. Open the Alerts tab and walk through the
three `PrometheusRule` alerts and what each is actually watching for.

## 4. GitOps (2 min)

Open ArgoCD (port-forward per RUNBOOK.md) - show the `learnops-production`
Application, its sync status, and the resource tree. Explain: nobody ran
`kubectl apply` for this - ArgoCD noticed the manifest change and did it.

## 5. CI/CD (1 min, once pushed to GitHub)

Open the GitHub Actions tab for a recent push - show
lint -> test -> build -> scan -> push -> promote, and point out the GHA
layer cache making the build step fast on a second run - the direct answer
to the brief's "35-minute rebuild-from-scratch" pain point.