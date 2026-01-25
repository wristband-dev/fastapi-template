# GitHub Secrets Module
# Automatically uploads all secrets to GitHub for CI/CD workflows

# Create GitHub Environments
resource "github_repository_environment" "staging" {
  repository  = var.repository_name
  environment = "STAGING"
}

resource "github_repository_environment" "prod" {
  repository  = var.repository_name
  environment = "PROD"
}

# Repository Secrets (accessible across all environments)
resource "github_actions_secret" "firebase_service_account_key" {
  repository      = var.repository_name
  secret_name     = "FIREBASE_SERVICE_ACCOUNT_KEY"
  plaintext_value = var.firebase_service_account_key
}

resource "github_actions_secret" "cloud_run_service_account_key" {
  repository      = var.repository_name
  secret_name     = "CLOUD_RUN_SERVICE_ACCOUNT_KEY"
  plaintext_value = var.cloud_run_service_account_key
}

resource "github_actions_secret" "vercel_token" {
  repository      = var.repository_name
  secret_name     = "VERCEL_TOKEN"
  plaintext_value = var.vercel_token
}

resource "github_actions_secret" "vercel_org_id" {
  repository      = var.repository_name
  secret_name     = "VERCEL_ORG_ID"
  plaintext_value = var.vercel_org_id
}

resource "github_actions_secret" "vercel_project_id" {
  repository      = var.repository_name
  secret_name     = "VERCEL_PROJECT_ID"
  plaintext_value = var.vercel_project_id
}

resource "github_actions_secret" "vercel_project_name" {
  repository      = var.repository_name
  secret_name     = "VERCEL_PROJECT_NAME"
  plaintext_value = var.vercel_project_name
}

# GCP Configuration Secrets (shared across all environments)
resource "github_actions_secret" "gcp_project_id" {
  repository      = var.repository_name
  secret_name     = "GCP_PROJECT_ID"
  plaintext_value = var.gcp_project_id
}

resource "github_actions_secret" "gcp_region" {
  repository      = var.repository_name
  secret_name     = "GCP_REGION"
  plaintext_value = var.gcp_region
}

resource "github_actions_secret" "gcp_api_name" {
  repository      = var.repository_name
  secret_name     = "GCP_API_NAME"
  plaintext_value = var.gcp_api_name
}

resource "github_actions_secret" "gcp_api_repo_name" {
  repository      = var.repository_name
  secret_name     = "GCP_API_REPO_NAME"
  plaintext_value = var.gcp_api_repo_name
}

# STAGING Environment Secrets
resource "github_actions_environment_secret" "staging_application_id" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "APPLICATION_ID"
  plaintext_value = var.staging_application_id
}

resource "github_actions_environment_secret" "staging_application_vanity_domain" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "APPLICATION_VANITY_DOMAIN"
  plaintext_value = var.staging_application_vanity_domain
}

resource "github_actions_environment_secret" "staging_client_id" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "CLIENT_ID"
  plaintext_value = var.staging_client_id
}

resource "github_actions_environment_secret" "staging_client_secret" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "CLIENT_SECRET"
  plaintext_value = var.staging_client_secret
}

resource "github_actions_environment_secret" "staging_domain_name" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "DOMAIN_NAME"
  plaintext_value = var.staging_domain_name
}

resource "github_actions_environment_secret" "staging_next_public_backend_url" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "NEXT_PUBLIC_BACKEND_URL"
  plaintext_value = var.staging_backend_url
}

resource "github_actions_environment_secret" "staging_next_public_application_signup_url" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "NEXT_PUBLIC_APPLICATION_SIGNUP_URL"
  plaintext_value = var.staging_signup_url
}

# PROD Environment Secrets
resource "github_actions_environment_secret" "prod_application_id" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "APPLICATION_ID"
  plaintext_value = var.prod_application_id
}

resource "github_actions_environment_secret" "prod_application_vanity_domain" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "APPLICATION_VANITY_DOMAIN"
  plaintext_value = var.prod_application_vanity_domain
}

resource "github_actions_environment_secret" "prod_client_id" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "CLIENT_ID"
  plaintext_value = var.prod_client_id
}

resource "github_actions_environment_secret" "prod_client_secret" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "CLIENT_SECRET"
  plaintext_value = var.prod_client_secret
}

resource "github_actions_environment_secret" "prod_domain_name" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "DOMAIN_NAME"
  plaintext_value = var.prod_domain_name != "" ? var.prod_domain_name : "${var.vercel_project_name}.vercel.app"
}

resource "github_actions_environment_secret" "prod_next_public_backend_url" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "NEXT_PUBLIC_BACKEND_URL"
  plaintext_value = var.prod_backend_url
}

resource "github_actions_environment_secret" "prod_next_public_application_signup_url" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "NEXT_PUBLIC_APPLICATION_SIGNUP_URL"
  plaintext_value = var.prod_signup_url
}

# Stripe Secrets (PROD)
resource "github_actions_environment_secret" "prod_stripe_secret_key" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "STRIPE_SECRET_KEY"
  plaintext_value = var.stripe_secret_key
}

resource "github_actions_environment_secret" "prod_stripe_price_id_pro" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "STRIPE_PRICE_ID_PRO"
  plaintext_value = var.stripe_price_id_pro
}

resource "github_actions_environment_secret" "prod_stripe_webhook_secret" {
  repository      = var.repository_name
  environment     = github_repository_environment.prod.environment
  secret_name     = "STRIPE_WEBHOOK_SECRET"
  plaintext_value = var.stripe_webhook_secret
}# Stripe Secrets (STAGING)
resource "github_actions_environment_secret" "staging_stripe_secret_key" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "STRIPE_SECRET_KEY"
  plaintext_value = var.stripe_secret_key
}

resource "github_actions_environment_secret" "staging_stripe_price_id_pro" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "STRIPE_PRICE_ID_PRO"
  plaintext_value = var.stripe_price_id_pro
}

resource "github_actions_environment_secret" "staging_stripe_webhook_secret" {
  repository      = var.repository_name
  environment     = github_repository_environment.staging.environment
  secret_name     = "STRIPE_WEBHOOK_SECRET"
  plaintext_value = var.stripe_webhook_secret
}
