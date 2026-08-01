resource "google_container_cluster" "learnops" {
  name     = "learnops-${var.environment}"
  location = var.region

  enable_autopilot = true

  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.id

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  deletion_protection = var.environment == "production"

  release_channel {
    channel = "REGULAR"
  }
}
