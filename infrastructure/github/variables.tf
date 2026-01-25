variable "repository_owner" {
  description = "GitHub repository owner (username or organization)"
  type        = string
}

variable "repository_name" {
  description = "GitHub repository name (without owner)"
  type        = string
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

# STAGING Environment Variables
variable "staging_application_id" {
  description = "Wristband application ID for STAGING"
  type        = string
}

variable "staging_application_vanity_domain" {
  description = "Wristband application vanity domain for STAGING"
  type        = string
}

variable "staging_client_id" {
  description = "Wristband OAuth2 client ID for STAGING"
  type        = string
}

variable "staging_client_secret" {
  description = "Wristband OAuth2 client secret for STAGING"
  type        = string
  sensitive   = true
}

variable "staging_domain_name" {
  description = "Frontend domain name for STAGING"
  type        = string
}

variable "staging_backend_url" {
  description = "Backend API URL for STAGING"
  type        = string
}

variable "staging_signup_url" {
  description = "Wristband signup URL for STAGING"
  type        = string
}

# PROD Environment Variables
variable "prod_application_id" {
  description = "Wristband application ID for PROD"
  type        = string
}

variable "prod_application_vanity_domain" {
  description = "Wristband application vanity domain for PROD"
  type        = string
}

variable "prod_client_id" {
  description = "Wristband OAuth2 client ID for PROD"
  type        = string
}

variable "prod_client_secret" {
  description = "Wristband OAuth2 client secret for PROD"
  type        = string
  sensitive   = true
}

variable "prod_domain_name" {
  description = "Frontend domain name for PROD"
  type        = string
}

variable "prod_backend_url" {
  description = "Backend API URL for PROD"
  type        = string
}

variable "prod_signup_url" {
  description = "Wristband signup URL for PROD"
  type        = string
}

# Stripe Variables
variable "stripe_secret_key" {
  description = "Stripe Secret Key"
  type        = string
  sensitive   = true
}

variable "stripe_price_id_pro" {
  description = "Stripe Price ID for Pro Plan"
  type        = string
}

variable "stripe_webhook_secret" {
  description = "Stripe Webhook Secret"
  type        = string
  sensitive   = true
}

# Repository Secrets
variable "firebase_service_account_key" {
  description = "Firebase service account key (base64 encoded)"
  type        = string
  sensitive   = true
}

variable "cloud_run_service_account_key" {
  description = "Cloud Run service account key (base64 encoded)"
  type        = string
  sensitive   = true
}

variable "vercel_token" {
  description = "Vercel API token"
  type        = string
  sensitive   = true
}

variable "vercel_org_id" {
  description = "Vercel organization ID"
  type        = string
}

variable "vercel_project_id" {
  description = "Vercel project ID"
  type        = string
}

variable "vercel_project_name" {
  description = "Vercel project name"
  type        = string
}

# GCP Configuration
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
}

variable "gcp_api_name" {
  description = "GCP API service name"
  type        = string
}

variable "gcp_api_repo_name" {
  description = "GCP Artifact Registry repository name"
  type        = string
}

