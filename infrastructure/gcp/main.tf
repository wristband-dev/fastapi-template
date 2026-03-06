# GCP Infrastructure Module

# Create the project if it doesn't exist
resource "google_project" "project" {
  name            = "${var.app_name} App"
  project_id      = var.project_id
  billing_account = var.billing_account_id
}

# Link the project to the billing account
resource "google_billing_project_info" "billing_link" {
  project         = google_project.project.project_id
  billing_account = var.billing_account_id

  depends_on = [google_project.project]
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "cloudbilling.googleapis.com",
    "domains.googleapis.com",
  ])

  project = google_project.project.project_id
  service = each.key

  disable_dependent_services = true
  disable_on_destroy         = false

  depends_on = [google_billing_project_info.billing_link]
}

# Wait for APIs to be fully propagated before creating dependent resources
resource "time_sleep" "wait_for_apis" {
  create_duration = "60s"

  depends_on = [google_project_service.services]
}

# Sanitized app name for GCP resource identifiers (no spaces)
# Cloud SQL: lowercase + hyphens; Secret Manager: lowercase + underscores
locals {
  app_name_resource = replace(lower(var.app_name), " ", "-")   # fast-api-template
  app_name_secret   = replace(replace(lower(var.app_name), " ", "_"), "-", "_")  # fast_api_template
}
