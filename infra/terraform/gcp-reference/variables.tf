variable "project_id" {
  description = "GCP project ID this module would deploy into. No default - never applied automatically."
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west2"
}

variable "environment" {
  description = "Environment name, drives sizing/HA decisions (production vs staging)"
  type        = string
  default     = "production"
}

variable "postgres_password" {
  description = "Password for the app's Postgres user (demo only - a real setup would source this from Secret Manager, not a Terraform variable)"
  type        = string
  sensitive   = true
}

variable "alert_email" {
  description = "Email address for Cloud Monitoring alert notifications"
  type        = string
}
