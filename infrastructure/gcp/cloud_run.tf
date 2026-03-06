# =============================================================================
# Cloud Run v2 — Production
# =============================================================================

resource "google_cloud_run_v2_service" "api_prod" {
  name     = "${var.project_id}-${var.api_name}"
  location = var.region
  project  = google_project.project.project_id

  template {
    # Cloud SQL connection via proxy
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.main.connection_name]
      }
    }

    containers {
      image = "gcr.io/cloudrun/hello"

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      env {
        name  = "ENVIRONMENT"
        value = "PROD"
      }
      env {
        name  = "DOMAIN_NAME"
        value = var.vercel_domain_name != "" ? var.vercel_domain_name : "${var.vercel_project_name}.vercel.app"
      }
      env {
        name  = "CLIENT_ID"
        value = var.wb_prod_client_id
      }
      env {
        name  = "CLIENT_SECRET"
        value = var.wb_prod_client_secret
      }
      env {
        name  = "APPLICATION_VANITY_DOMAIN"
        value = var.wb_prod_application_vanity_domain
      }
      env {
        name  = "APPLICATION_ID"
        value = var.wb_prod_app_id
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url_prod.secret_id
            version = google_secret_manager_secret_version.database_url_prod.version
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    service_account = google_service_account.cloud_run_sa.email
  }

  depends_on = [
    google_project_service.services["run.googleapis.com"],
    google_artifact_registry_repository.api_repo,
    google_secret_manager_secret_iam_member.cloud_run_db_url_prod,
    google_secret_manager_secret_version.database_url_prod,
    time_sleep.wait_for_cloud_run_iam,
    time_sleep.wait_for_artifact_registry_iam,
  ]

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Allow unauthenticated access (Production)
resource "google_cloud_run_v2_service_iam_member" "public_access_prod" {
  name     = google_cloud_run_v2_service.api_prod.name
  location = google_cloud_run_v2_service.api_prod.location
  project  = google_project.project.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run v2 — Staging
# =============================================================================

resource "google_cloud_run_v2_service" "api_staging" {
  name     = "${var.project_id}-${var.api_name}-staging"
  location = var.region
  project  = google_project.project.project_id

  template {
    # Cloud SQL connection via proxy
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.main.connection_name]
      }
    }

    containers {
      image = "gcr.io/cloudrun/hello"

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      env {
        name  = "ENVIRONMENT"
        value = "STAGING"
      }
      env {
        name  = "DOMAIN_NAME"
        value = var.vercel_project_name != "" ? "staging-${var.vercel_project_name}.vercel.app" : ""
      }
      env {
        name  = "CLIENT_ID"
        value = var.wb_staging_client_id
      }
      env {
        name  = "CLIENT_SECRET"
        value = var.wb_staging_client_secret
      }
      env {
        name  = "APPLICATION_VANITY_DOMAIN"
        value = var.wb_staging_application_vanity_domain
      }
      env {
        name  = "APPLICATION_ID"
        value = var.wb_staging_app_id
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url_staging.secret_id
            version = google_secret_manager_secret_version.database_url_staging.version
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    service_account = google_service_account.cloud_run_sa.email
  }

  depends_on = [
    google_project_service.services["run.googleapis.com"],
    google_artifact_registry_repository.api_repo,
    google_secret_manager_secret_iam_member.cloud_run_db_url_staging,
    google_secret_manager_secret_version.database_url_staging,
    time_sleep.wait_for_cloud_run_iam,
    time_sleep.wait_for_artifact_registry_iam,
  ]

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Allow unauthenticated access (Staging)
resource "google_cloud_run_v2_service_iam_member" "public_access_staging" {
  name     = google_cloud_run_v2_service.api_staging.name
  location = google_cloud_run_v2_service.api_staging.location
  project  = google_project.project.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}
