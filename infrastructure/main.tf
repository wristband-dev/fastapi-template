terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    restapi = {
      source  = "Mastercard/restapi"
      version = "~> 1.18"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.4"
    }
    stripe = {
      source  = "lukasaron/stripe"
      version = "~> 2.0"
    }
  }
  required_version = ">= 1.0"
}

# Configure Stripe Provider (uses test key for creating products/prices)
provider "stripe" {
  api_key = var.stripe_test_api_key
}

# Configure Google Cloud Provider
provider "google" {
  region = var.gcp_region
}

provider "google-beta" {
  region = var.gcp_region
}

# Configure Vercel Provider
# Use a valid dummy token format when deployment is disabled to avoid validation errors
provider "vercel" {
  api_token = var.deployment_enabled && var.vercel_api_token != "" && length(var.vercel_api_token) == 24 ? var.vercel_api_token : "000000000000000000000000"
}

# Configure GitHub Provider (for secrets management)
provider "github" {
  token = var.github_token != "" ? var.github_token : null
  owner = local.github_repo_owner
}

# Get OAuth tokens for Wristband environments
data "http" "wristband_dev_token" {
  count = var.wb_dev_application_vanity_domain != "" ? 1 : 0
  
  url    = "https://${var.wb_dev_application_vanity_domain}/api/v1/oauth2/token"
  method = "POST"
  
  request_headers = {
    "Content-Type"  = "application/x-www-form-urlencoded"
    "Authorization" = "Basic ${base64encode("${var.wb_dev_client_id}:${var.wb_dev_client_secret}")}"
  }
  
  request_body = "grant_type=client_credentials"
}

data "http" "wristband_staging_token" {
  count = var.deployment_enabled && var.wb_staging_application_vanity_domain != "" ? 1 : 0
  
  url    = "https://${var.wb_staging_application_vanity_domain}/api/v1/oauth2/token"
  method = "POST"
  
  request_headers = {
    "Content-Type"  = "application/x-www-form-urlencoded"
    "Authorization" = "Basic ${base64encode("${var.wb_staging_client_id}:${var.wb_staging_client_secret}")}"
  }
  
  request_body = "grant_type=client_credentials"
}

data "http" "wristband_prod_token" {
  count = var.deployment_enabled && var.wb_prod_application_vanity_domain != "" ? 1 : 0
  
  url    = "https://${var.wb_prod_application_vanity_domain}/api/v1/oauth2/token"
  method = "POST"
  
  request_headers = {
    "Content-Type"  = "application/x-www-form-urlencoded"
    "Authorization" = "Basic ${base64encode("${var.wb_prod_client_id}:${var.wb_prod_client_secret}")}"
  }
  
  request_body = "grant_type=client_credentials"
}

# Parse GitHub repository (supports both "owner/repo" and "https://github.com/owner/repo.git" formats)
locals {
  # Extract owner/repo from URL or use as-is
  github_repo_parsed = (
    can(regex("^https://", var.github_repository)) ?
    trim(replace(replace(var.github_repository, "https://github.com/", ""), ".git", ""), "/") :
    var.github_repository
  )
  github_repo_owner = split("/", local.github_repo_parsed)[0]
  github_repo_name  = split("/", local.github_repo_parsed)[1]
}

# Extract application IDs from OAuth tokens
locals {
  wb_dev_token = length(data.http.wristband_dev_token) > 0 ? jsondecode(data.http.wristband_dev_token[0].response_body).access_token : ""
  wb_dev_token_parts = local.wb_dev_token != "" ? split(".", local.wb_dev_token) : ["", "", ""]
  wb_dev_padding_count = local.wb_dev_token != "" ? ((4 - length(local.wb_dev_token_parts[1]) % 4) % 4) : 0
  wb_dev_payload_padded = local.wb_dev_token != "" ? "${local.wb_dev_token_parts[1]}${join("", [for i in range(local.wb_dev_padding_count) : "="])}" : ""
  wb_dev_token_payload = local.wb_dev_payload_padded != "" ? jsondecode(base64decode(local.wb_dev_payload_padded)) : {}
  wb_dev_app_id = try(coalesce(
    try(local.wb_dev_token_payload.aud, null),
    try(local.wb_dev_token_payload.app_id, null),
    try(local.wb_dev_token_payload.application_id, null)
  ), "")
  
  wb_staging_token = length(data.http.wristband_staging_token) > 0 ? jsondecode(data.http.wristband_staging_token[0].response_body).access_token : ""
  wb_staging_token_parts = local.wb_staging_token != "" ? split(".", local.wb_staging_token) : ["", "", ""]
  wb_staging_padding_count = local.wb_staging_token != "" ? ((4 - length(local.wb_staging_token_parts[1]) % 4) % 4) : 0
  wb_staging_payload_padded = local.wb_staging_token != "" ? "${local.wb_staging_token_parts[1]}${join("", [for i in range(local.wb_staging_padding_count) : "="])}" : ""
  wb_staging_token_payload = local.wb_staging_payload_padded != "" ? jsondecode(base64decode(local.wb_staging_payload_padded)) : {}
  wb_staging_app_id = try(coalesce(
    try(local.wb_staging_token_payload.aud, null),
    try(local.wb_staging_token_payload.app_id, null),
    try(local.wb_staging_token_payload.application_id, null)
  ), "")
  
  wb_prod_token = length(data.http.wristband_prod_token) > 0 ? jsondecode(data.http.wristband_prod_token[0].response_body).access_token : ""
  wb_prod_token_parts = local.wb_prod_token != "" ? split(".", local.wb_prod_token) : ["", "", ""]
  wb_prod_padding_count = local.wb_prod_token != "" ? ((4 - length(local.wb_prod_token_parts[1]) % 4) % 4) : 0
  wb_prod_payload_padded = local.wb_prod_token != "" ? "${local.wb_prod_token_parts[1]}${join("", [for i in range(local.wb_prod_padding_count) : "="])}" : ""
  wb_prod_token_payload = local.wb_prod_payload_padded != "" ? jsondecode(base64decode(local.wb_prod_payload_padded)) : {}
  wb_prod_app_id = try(coalesce(
    try(local.wb_prod_token_payload.aud, null),
    try(local.wb_prod_token_payload.app_id, null),
    try(local.wb_prod_token_payload.application_id, null)
  ), "")
}

# Configure REST API providers for each Wristband environment
provider "restapi" {
  alias = "wristband_dev"
  
  uri                   = var.wb_dev_application_vanity_domain != "" ? "https://${var.wb_dev_application_vanity_domain}/api/v1" : "https://placeholder.wristband.dev/api/v1"
  write_returns_object  = true
  create_returns_object = true
  
  headers = local.wb_dev_token != "" ? {
    "Authorization" = "Bearer ${local.wb_dev_token}"
    "Content-Type"  = "application/json"
  } : {}
}

provider "restapi" {
  alias = "wristband_staging"
  
  uri                   = var.wb_staging_application_vanity_domain != "" ? "https://${var.wb_staging_application_vanity_domain}/api/v1" : "https://placeholder.wristband.dev/api/v1"
  write_returns_object  = true
  create_returns_object = true
  
  headers = local.wb_staging_token != "" ? {
    "Authorization" = "Bearer ${local.wb_staging_token}"
    "Content-Type"  = "application/json"
  } : {}
}

provider "restapi" {
  alias = "wristband_prod"
  
  uri                   = var.wb_prod_application_vanity_domain != "" ? "https://${var.wb_prod_application_vanity_domain}/api/v1" : "https://placeholder.wristband.dev/api/v1"
  write_returns_object  = true
  create_returns_object = true
  
  headers = local.wb_prod_token != "" ? {
    "Authorization" = "Bearer ${local.wb_prod_token}"
    "Content-Type"  = "application/json"
  } : {}
}

# Stripe Module
module "stripe" {
  source = "./stripe"
  product_name = var.gcp_app_name
  # Webhook URL: Set manually after deployment, or leave empty to skip webhook creation
  # You can update this later with your actual backend URL (e.g., "https://api.yourdomain.com")
  webhook_url  = ""
}

# GCP Module (only if deployment enabled)
module "gcp" {
  source = "./gcp"
  count  = var.deployment_enabled ? 1 : 0

  project_id         = var.gcp_project_id
  billing_account_id = var.gcp_billing_account_id
  region             = var.gcp_region
  firestore_location = var.gcp_firestore_location
  app_name           = var.gcp_app_name
  api_name           = var.gcp_api_name
  api_repo_name      = var.gcp_api_repo_name
  
  # Wristband Staging variables
  wb_staging_application_vanity_domain = var.wb_staging_application_vanity_domain
  wb_staging_client_id                 = var.wb_staging_client_id
  wb_staging_client_secret             = var.wb_staging_client_secret
  wb_staging_app_id                    = local.wb_staging_app_id
  
  # Wristband Prod variables
  wb_prod_application_vanity_domain = var.wb_prod_application_vanity_domain
  wb_prod_client_id                 = var.wb_prod_client_id
  wb_prod_client_secret             = var.wb_prod_client_secret
  wb_prod_app_id                    = local.wb_prod_app_id
  
  # Vercel variables
  vercel_project_name = var.vercel_project_name
  vercel_domain_name  = var.vercel_domain_name
}

# Vercel Module (only if deployment enabled)
module "vercel" {
  source = "./vercel"
  count  = var.deployment_enabled ? 1 : 0

  vercel_api_token    = var.vercel_api_token
  vercel_project_name = var.vercel_project_name
  vercel_domain_name  = var.vercel_domain_name
  cloud_run_url       = var.deployment_enabled && length(module.gcp) > 0 ? module.gcp[0].cloud_run_prod_url : "http://localhost:6001"
}

# Wristband Module - DEV (always enabled if credentials provided)
module "wristband_dev" {
  source = "./wristband"
  count  = var.wb_dev_application_vanity_domain != "" ? 1 : 0

  application_vanity_domain = var.wb_dev_application_vanity_domain
  client_id                 = var.wb_dev_client_id
  client_secret             = var.wb_dev_client_secret
  application_id            = local.wb_dev_app_id
  access_token              = local.wb_dev_token
  environment               = "dev"
  frontend_url              = "http://localhost:3001"
  backend_url               = "http://localhost:6001"
  self_signup_enabled       = true
  logo_url                  = var.logo_url
  color                     = var.color
  
  providers = {
    restapi = restapi.wristband_dev
  }
}

# Wristband Module - STAGING (only if deployment enabled)
module "wristband_staging" {
  source = "./wristband"
  count  = var.deployment_enabled && var.wb_staging_application_vanity_domain != "" ? 1 : 0

  application_vanity_domain = var.wb_staging_application_vanity_domain
  client_id                 = var.wb_staging_client_id
  client_secret             = var.wb_staging_client_secret
  application_id            = local.wb_staging_app_id
  access_token              = local.wb_staging_token
  environment               = "staging"
  frontend_url              = "https://staging-${var.vercel_project_name}.vercel.app"
  backend_url               = var.deployment_enabled && length(module.gcp) > 0 ? module.gcp[0].cloud_run_staging_url : "http://localhost:6001"
  self_signup_enabled       = true
  logo_url                  = var.logo_url
  color                     = var.color
  
  providers = {
    restapi = restapi.wristband_staging
  }
  
  depends_on = [module.gcp, module.vercel]
}

# Wristband Module - PROD (only if deployment enabled)
module "wristband_prod" {
  source = "./wristband"
  count  = var.deployment_enabled && var.wb_prod_application_vanity_domain != "" ? 1 : 0

  application_vanity_domain = var.wb_prod_application_vanity_domain
  client_id                 = var.wb_prod_client_id
  client_secret             = var.wb_prod_client_secret
  application_id            = local.wb_prod_app_id
  access_token              = local.wb_prod_token
  environment               = "prod"
  frontend_url              = var.vercel_domain_name != "" ? "https://${var.vercel_domain_name}" : "https://${var.vercel_project_name}.vercel.app"
  backend_url               = var.deployment_enabled && length(module.gcp) > 0 ? module.gcp[0].cloud_run_prod_url : "http://localhost:6001"
  self_signup_enabled       = true
  logo_url                  = var.logo_url
  color                     = var.color
  
  providers = {
    restapi = restapi.wristband_prod
  }
  
  depends_on = [module.gcp, module.vercel]
}

# GitHub Module (only if deployment enabled and token provided)
module "github" {
  source = "./github"
  count  = var.deployment_enabled && var.github_token != "" ? 1 : 0

  providers = {
    github = github
  }

  repository_owner = local.github_repo_owner
  repository_name  = local.github_repo_name
  github_token     = var.github_token

  # STAGING Environment Secrets
  staging_application_id              = length(module.wristband_staging) > 0 ? module.wristband_staging[0].application_id : ""
  staging_application_vanity_domain   = var.wb_staging_application_vanity_domain
  staging_client_id                   = length(module.wristband_staging) > 0 ? module.wristband_staging[0].oauth2_client_id : ""
  staging_client_secret               = length(module.wristband_staging) > 0 ? module.wristband_staging[0].oauth2_client_secret : ""
  staging_domain_name                 = "staging-${var.vercel_project_name}.vercel.app"
  staging_backend_url                 = length(module.gcp) > 0 ? module.gcp[0].cloud_run_staging_url : ""
  staging_signup_url                  = "https://${var.wb_staging_application_vanity_domain}/signup"

  # PROD Environment Secrets
  prod_application_id                 = length(module.wristband_prod) > 0 ? module.wristband_prod[0].application_id : ""
  prod_application_vanity_domain      = var.wb_prod_application_vanity_domain
  prod_client_id                      = length(module.wristband_prod) > 0 ? module.wristband_prod[0].oauth2_client_id : ""
  prod_client_secret                  = length(module.wristband_prod) > 0 ? module.wristband_prod[0].oauth2_client_secret : ""
  prod_domain_name                    = var.vercel_domain_name
  prod_backend_url                    = length(module.gcp) > 0 ? module.gcp[0].cloud_run_prod_url : ""
  prod_signup_url                     = "https://${var.wb_prod_application_vanity_domain}/signup"

  # Stripe Secrets
  stripe_secret_key_staging = var.stripe_test_api_key
  stripe_secret_key_prod    = var.stripe_prod_api_key
  stripe_price_id_pro       = module.stripe.price_id_pro
  stripe_webhook_secret     = module.stripe.webhook_secret

  # Repository Secrets
  firebase_service_account_key     = length(module.gcp) > 0 ? module.gcp[0].firebase_service_account_key : ""
  cloud_run_service_account_key    = length(module.gcp) > 0 ? module.gcp[0].cloud_run_service_account_key : ""
  vercel_token                     = var.vercel_api_token
  vercel_org_id                    = var.vercel_org_id
  vercel_project_id                = length(module.vercel) > 0 ? module.vercel[0].vercel_project_id : ""
  vercel_project_name              = var.vercel_project_name
  gcp_project_id                   = var.gcp_project_id
  gcp_region                       = var.gcp_region
  gcp_api_name                     = var.gcp_api_name
  gcp_api_repo_name                = var.gcp_api_repo_name

  depends_on = [module.gcp, module.vercel, module.wristband_staging, module.wristband_prod, module.stripe]
}

