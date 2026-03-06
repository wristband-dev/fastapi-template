# =============================================================================
# CLOUD SQL - PostgreSQL (Staging + Prod)
# Local dev uses Docker - see backend/docker-compose.yml
# =============================================================================

# Generate database passwords
resource "random_password" "db_password_staging" {
  length  = 24
  special = false
}

resource "random_password" "db_password_prod" {
  length  = 24
  special = false
}

# Cloud SQL Instance (shared by staging + prod)
resource "google_sql_database_instance" "main" {
  name                = "${local.app_name_resource}-db"
  project             = google_project.project.project_id
  database_version    = var.db_version
  region              = var.region
  deletion_protection = var.db_deletion_protection

  settings {
    tier      = var.db_tier
    disk_size = 10
    disk_type = "PD_SSD"

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled = true
    }

    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  depends_on = [time_sleep.wait_for_apis]
}

# =============================================================================
# IAM DATABASE USERS
# Users can authenticate via Cloud SQL Studio using their Google account
# =============================================================================

resource "google_sql_user" "iam_users" {
  for_each = toset(var.db_iam_users)

  name     = each.value
  instance = google_sql_database_instance.main.name
  type     = "CLOUD_IAM_USER"
  project  = google_project.project.project_id
}

# =============================================================================
# STAGING DATABASE
# =============================================================================

resource "google_sql_database" "staging" {
  name     = "${local.app_name_resource}-staging"
  instance = google_sql_database_instance.main.name
  project  = google_project.project.project_id
}

resource "google_sql_user" "staging" {
  name     = "${local.app_name_resource}-staging"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password_staging.result
  project  = google_project.project.project_id
}

# =============================================================================
# PROD DATABASE
# =============================================================================

resource "google_sql_database" "prod" {
  name     = "${local.app_name_resource}-prod"
  instance = google_sql_database_instance.main.name
  project  = google_project.project.project_id
}

resource "google_sql_user" "prod" {
  name     = "${local.app_name_resource}-prod"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password_prod.result
  project  = google_project.project.project_id
}

# =============================================================================
# SECRET MANAGER - DATABASE URLs
# =============================================================================

# Staging
resource "google_secret_manager_secret" "database_url_staging" {
  project   = google_project.project.project_id
  secret_id = "${local.app_name_secret}_database_url_staging"

  replication {
    auto {}
  }

  depends_on = [time_sleep.wait_for_apis]
}

resource "google_secret_manager_secret_version" "database_url_staging" {
  secret = google_secret_manager_secret.database_url_staging.id
  secret_data = format(
    "postgresql://%s:%s@/%s?host=/cloudsql/%s",
    google_sql_user.staging.name,
    random_password.db_password_staging.result,
    google_sql_database.staging.name,
    google_sql_database_instance.main.connection_name
  )
}

# Prod
resource "google_secret_manager_secret" "database_url_prod" {
  project   = google_project.project.project_id
  secret_id = "${local.app_name_secret}_database_url_prod"

  replication {
    auto {}
  }

  depends_on = [time_sleep.wait_for_apis]
}

resource "google_secret_manager_secret_version" "database_url_prod" {
  secret = google_secret_manager_secret.database_url_prod.id
  secret_data = format(
    "postgresql://%s:%s@/%s?host=/cloudsql/%s",
    google_sql_user.prod.name,
    random_password.db_password_prod.result,
    google_sql_database.prod.name,
    google_sql_database_instance.main.connection_name
  )
}
