# Private IP requires a VPC peering range reserved for Google-managed services.
resource "google_compute_global_address" "private_ip_range" {
  name          = "learnops-${var.environment}-sql-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

resource "google_sql_database_instance" "learnops" {
  name                = "learnops-${var.environment}"
  database_version    = "POSTGRES_16"
  region              = var.region
  deletion_protection = var.environment == "production"

  depends_on = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier              = "db-f1-micro"
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = var.environment == "production"
    }
  }
}

resource "google_sql_database" "learnops" {
  name     = "learnops"
  instance = google_sql_database_instance.learnops.name
}

resource "google_sql_user" "app" {
  name     = "learnops"
  instance = google_sql_database_instance.learnops.name
  password = var.postgres_password
}
