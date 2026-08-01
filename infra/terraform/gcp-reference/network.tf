# VPC-native networking for GKE. A real environment would likely also add
# Cloud NAT for private-node egress and tighter firewall rules than GKE's
# defaults - omitted here to keep this reference focused.

resource "google_compute_network" "vpc" {
  name                    = "learnops-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "learnops-${var.environment}-gke"
  network       = google_compute_network.vpc.id
  region        = var.region
  ip_cidr_range = "10.10.0.0/20"

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.20.0.0/14"
  }
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.30.0.0/20"
  }
}
