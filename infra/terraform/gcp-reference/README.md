# GCP-reference (documentation only - never applied)

This module is **not part of the working demo** and is never run by CI or
any script in this repo. It exists to show what migrating this platform
onto real GCP infrastructure would look like in Terraform, mapped directly
onto the local `kind`-based setup in `infra/terraform/local`:

| Local (kind)                        | GCP equivalent                            | File                   |
|--------------------------------------|--------------------------------------------|------------------------|
| `kind` cluster                       | GKE Autopilot cluster                      | `gke.tf`               |
| `postgres.yaml` Deployment           | Cloud SQL (Postgres 16, private IP)        | `cloudsql.tf`          |
| `redis.yaml` Deployment              | Memorystore (Redis 7.2, BASIC tier)        | `redis.tf`             |
| GHCR (via CI)                        | Artifact Registry                          | `artifact-registry.tf` |
| Manual `kubectl logs` digging        | Log-based metric + Cloud Monitoring alert  | `logging.tf`           |
| n/a (no cluster networking locally)  | VPC + subnet with secondary ranges         | `network.tf`           |

Running this for real requires the Google Cloud SDK (`gcloud`) installed and
authenticated, a GCP project with billing enabled, and `terraform apply` run
manually by a human who's reviewed the plan - never automatically. Given the
ongoing cost of GKE/Cloud SQL/Memorystore, that's a deliberate choice: this
repo demonstrates the Terraform, but doesn't run it against a live billing
account.

## Deliberately out of scope here

- IAM/Workload Identity bindings between GKE and Cloud SQL/Artifact
  Registry - a real rollout needs these; omitted to keep this reference
  focused on the resource-level mapping.
- Cloud NAT / tighter firewall rules than GKE's defaults.
- Multi-region HA beyond Cloud SQL's own `REGIONAL` availability setting.
