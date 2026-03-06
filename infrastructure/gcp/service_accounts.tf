# =============================================================================
# Cloud Run Service Account
# =============================================================================

resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-service"
  display_name = "Cloud Run Service Account"
  description  = "Service account for Cloud Run services"
  project      = google_project.project.project_id

  depends_on = [time_sleep.wait_for_apis]
}

# Grant Cloud Run Invoker role
resource "google_project_iam_member" "cloud_run_invoker_role" {
  project = google_project.project.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Cloud SQL Client role (connect to Cloud SQL via proxy)
resource "google_project_iam_member" "cloud_run_sql_client" {
  project = google_project.project.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant service usage consumer role
resource "google_project_iam_member" "cloud_run_service_usage_consumer" {
  project = google_project.project.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Cloud Run Admin role (to deploy services)
resource "google_project_iam_member" "cloud_run_admin" {
  project = google_project.project.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Project IAM Admin role for Cloud Run service creation
resource "google_project_iam_member" "cloud_run_iam_admin" {
  project = google_project.project.project_id
  role    = "roles/resourcemanager.projectIamAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant IAM Service Account User role
resource "google_project_iam_member" "service_account_user" {
  project = google_project.project.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Cloud Build Editor role
resource "google_project_iam_member" "cloud_build_editor" {
  project = google_project.project.project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Wait for Cloud Run IAM bindings to propagate
resource "time_sleep" "wait_for_cloud_run_iam" {
  create_duration = "30s"

  depends_on = [
    google_project_iam_member.cloud_run_invoker_role,
    google_project_iam_member.cloud_run_sql_client,
    google_project_iam_member.cloud_run_service_usage_consumer,
    google_project_iam_member.cloud_run_admin,
    google_project_iam_member.cloud_run_iam_admin,
    google_project_iam_member.service_account_user,
    google_project_iam_member.cloud_build_editor,
  ]
}

# Create Cloud Run service account key (for CI/CD deployments)
resource "google_service_account_key" "cloud_run_key" {
  service_account_id = google_service_account.cloud_run_sa.name

  depends_on = [time_sleep.wait_for_cloud_run_iam]
}

# =============================================================================
# Secret Manager Access — Cloud Run reads DATABASE_URL from Secret Manager
# =============================================================================

resource "google_secret_manager_secret_iam_member" "cloud_run_db_url_staging" {
  project   = google_project.project.project_id
  secret_id = google_secret_manager_secret.database_url_staging.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_db_url_prod" {
  project   = google_project.project.project_id
  secret_id = google_secret_manager_secret.database_url_prod.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# =============================================================================
# IAM Database Authentication (Cloud SQL Studio access)
# =============================================================================

resource "google_project_iam_member" "sql_iam_users" {
  for_each = toset(var.db_iam_users)

  project = google_project.project.project_id
  role    = "roles/cloudsql.instanceUser"
  member  = "user:${each.value}"
}

resource "google_project_iam_member" "sql_iam_clients" {
  for_each = toset(var.db_iam_users)

  project = google_project.project.project_id
  role    = "roles/cloudsql.client"
  member  = "user:${each.value}"
}
