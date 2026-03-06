output "project_id" {
  description = "The GCP project ID"
  value       = google_project.project.project_id
}

output "project_number" {
  description = "The GCP project number"
  value       = google_project.project.number
}

# Cloud SQL outputs
output "cloud_sql_instance_name" {
  description = "The Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "cloud_sql_connection_name" {
  description = "The Cloud SQL instance connection name (for Cloud SQL Proxy)"
  value       = google_sql_database_instance.main.connection_name
}

# Cloud Run outputs
output "cloud_run_service_account" {
  description = "The Cloud Run service account email"
  value       = google_service_account.cloud_run_sa.email
}

output "cloud_run_service_account_key" {
  description = "The Cloud Run service account key (base64-encoded)"
  value       = google_service_account_key.cloud_run_key.private_key
  sensitive   = true
}

output "artifact_registry_repository_id" {
  description = "The Artifact Registry repository ID"
  value       = google_artifact_registry_repository.api_repo.repository_id
}

output "artifact_registry_repository_url" {
  description = "The Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${google_project.project.project_id}/${google_artifact_registry_repository.api_repo.repository_id}"
}

output "cloud_run_prod_url" {
  description = "The URL of the deployed Cloud Run service (Production)"
  value       = google_cloud_run_v2_service.api_prod.uri
}

output "cloud_run_staging_url" {
  description = "The URL of the deployed Cloud Run service (Staging)"
  value       = google_cloud_run_v2_service.api_staging.uri
}

output "cloud_run_prod_service_name" {
  description = "The name of the Cloud Run service (Production)"
  value       = google_cloud_run_v2_service.api_prod.name
}

output "cloud_run_staging_service_name" {
  description = "The name of the Cloud Run service (Staging)"
  value       = google_cloud_run_v2_service.api_staging.name
}
