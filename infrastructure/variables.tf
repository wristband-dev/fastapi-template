# Wristband Variables
variable "wb_dev_application_vanity_domain" {
  description = "Wristband DEV application vanity domain"
  type        = string
  default     = ""
}

variable "wb_dev_client_id" {
  description = "Wristband DEV client ID"
  type        = string
  default     = ""
}

variable "wb_dev_client_secret" {
  description = "Wristband DEV client secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "wb_staging_application_vanity_domain" {
  description = "Wristband STAGING application vanity domain"
  type        = string
  default     = ""
}

variable "wb_staging_client_id" {
  description = "Wristband STAGING client ID"
  type        = string
  default     = ""
}

variable "wb_staging_client_secret" {
  description = "Wristband STAGING client secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "wb_prod_application_vanity_domain" {
  description = "Wristband PROD application vanity domain"
  type        = string
  default     = ""
}

variable "wb_prod_client_id" {
  description = "Wristband PROD client ID"
  type        = string
  default     = ""
}

variable "wb_prod_client_secret" {
  description = "Wristband PROD client secret"
  type        = string
  sensitive   = true
  default     = ""
}

# Stripe Variables
variable "stripe_test_api_key" {
  description = "Stripe Test Secret Key (sk_test_...) - used for DEV and STAGING"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_prod_api_key" {
  description = "Stripe Production Secret Key (sk_live_...) - used for PROD"
  type        = string
  sensitive   = true
  default     = ""
}

# Deployment Control
variable "deploy_cloud_infrastructure" {
  description = "Enable deployment infrastructure (GCP, Vercel, GitHub, Wristband Staging/Prod). Set to false for local dev only."
  type        = bool
  default     = false
}

# GCP Variables
variable "gcp_project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "gcp_billing_account_id" {
  description = "The GCP billing account ID"
  type        = string
}

variable "gcp_region" {
  description = "The default GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "gcp_app_name" {
  description = "The base name of the application (used in resource naming)"
  type        = string
}

variable "gcp_api_name" {
  description = "The name of the API component"
  type        = string
  default     = "api"
}

variable "gcp_api_repo_name" {
  description = "The name of the API repository"
  type        = string
  default     = "api-repo"
}

# Cloud SQL Variables
variable "gcp_db_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-f1-micro"
}

variable "gcp_db_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "POSTGRES_16"
}

variable "gcp_db_deletion_protection" {
  description = "Prevent accidental deletion of the Cloud SQL instance"
  type        = bool
  default     = true
}

variable "gcp_db_iam_users" {
  description = "List of IAM user emails for Cloud SQL IAM authentication"
  type        = list(string)
  default     = []
}

# Vercel Variables
variable "vercel_api_token" {
  description = "Vercel API token for authentication (optional - will use Vercel CLI auth if not provided)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "vercel_org_id" {
  description = "Vercel organization/team ID (format: team_XXX...)"
  type        = string
  default     = ""
}

variable "vercel_project_name" {
  description = "The name of your existing Vercel project (must be created manually first)"
  type        = string
  default     = ""
}

variable "vercel_domain_name" {
  description = "The custom domain to link to the Vercel project"
  type        = string
  default     = ""
}

# GitHub Variables
variable "github_token" {
  description = "GitHub personal access token for managing secrets (optional - will use GITHUB_TOKEN env var if not provided)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "github_repository" {
  description = "GitHub repository in format 'owner/repo' (e.g., 'fddiferd/score-keeper')"
  type        = string
  default     = "fddiferd/score-keeper"
}

# Branding Variables (Page & Email)
variable "logo_url" {
  description = "URL for the brand logo in page branding and email branding"
  type        = string
  default     = ""
}

variable "color" {
  description = "Primary brand color for page branding and email branding (hex color code)"
  type        = string
  default     = "#007bff"
}

