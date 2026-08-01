# Where CI would push images in a real GCP deployment, instead of GHCR.

resource "google_artifact_registry_repository" "learnops" {
  location      = var.region
  repository_id = "learnops"
  format        = "DOCKER"
}
