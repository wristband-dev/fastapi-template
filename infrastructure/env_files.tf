# Generate .env files for each environment

# DEV Environment
resource "local_file" "env_dev" {
  count = var.wb_dev_application_vanity_domain != "" ? 1 : 0
  
  filename = "${path.module}/../backend/.env.local"
  
  content = <<-EOT
ENVIRONMENT="DEV"
CLIENT_ID="${module.wristband_dev[0].oauth2_client_id}"
CLIENT_SECRET="${module.wristband_dev[0].oauth2_client_secret}"
APPLICATION_VANITY_DOMAIN="${var.wb_dev_application_vanity_domain}"
APPLICATION_ID="${local.wb_dev_app_id}"
STRIPE_SECRET_KEY="${var.stripe_test_api_key}"
${var.deployment_enabled ? "FIREBASE_SERVICE_ACCOUNT_KEY=\"${module.gcp[0].firebase_service_account_key}\"" : ""}
${var.deployment_enabled ? "CLOUD_RUN_SERVICE_ACCOUNT_KEY=\"${module.gcp[0].cloud_run_service_account_key}\"" : ""}
EOT

  file_permission = "0600"
  
  depends_on = [module.wristband_dev]
}

# STAGING Environment
resource "local_file" "env_staging" {
  count = var.deployment_enabled && var.wb_staging_application_vanity_domain != "" ? 1 : 0
  
  filename = "${path.module}/../backend/.env.staging"
  
  content = <<-EOT
ENVIRONMENT="STAGING"
DOMAIN_NAME="staging-${var.vercel_project_name}.vercel.app"
CLIENT_ID="${module.wristband_staging[0].oauth2_client_id}"
CLIENT_SECRET="${module.wristband_staging[0].oauth2_client_secret}"
APPLICATION_VANITY_DOMAIN="${var.wb_staging_application_vanity_domain}"
APPLICATION_ID="${local.wb_staging_app_id}"
STRIPE_SECRET_KEY="${var.stripe_test_api_key}"
FIREBASE_SERVICE_ACCOUNT_KEY="${module.gcp[0].firebase_service_account_key}"
CLOUD_RUN_SERVICE_ACCOUNT_KEY="${module.gcp[0].cloud_run_service_account_key}"
GCP_PROJECT_ID="${var.gcp_project_id}"
GCP_REGION="${var.gcp_region}"
GCP_API_NAME="${var.gcp_api_name}"
GCP_API_REPO_NAME="${var.gcp_api_repo_name}"
EOT

  file_permission = "0600"
  
  depends_on = [module.gcp, module.vercel, module.wristband_staging]
}

# PRODUCTION Environment
resource "local_file" "env_prod" {
  count = var.deployment_enabled && var.wb_prod_application_vanity_domain != "" ? 1 : 0
  
  filename = "${path.module}/../backend/.env.prod"
  
  content = <<-EOT
ENVIRONMENT="PROD"
DOMAIN_NAME="${var.vercel_domain_name != "" ? var.vercel_domain_name : "${var.vercel_project_name}.vercel.app"}"
CLIENT_ID="${module.wristband_prod[0].oauth2_client_id}"
CLIENT_SECRET="${module.wristband_prod[0].oauth2_client_secret}"
APPLICATION_VANITY_DOMAIN="${var.wb_prod_application_vanity_domain}"
APPLICATION_ID="${local.wb_prod_app_id}"
STRIPE_SECRET_KEY="${var.stripe_prod_api_key}"
FIREBASE_SERVICE_ACCOUNT_KEY="${module.gcp[0].firebase_service_account_key}"
CLOUD_RUN_SERVICE_ACCOUNT_KEY="${module.gcp[0].cloud_run_service_account_key}"
GCP_PROJECT_ID="${var.gcp_project_id}"
GCP_REGION="${var.gcp_region}"
GCP_API_NAME="${var.gcp_api_name}"
GCP_API_REPO_NAME="${var.gcp_api_repo_name}"
EOT

  file_permission = "0600"
  
  depends_on = [module.gcp, module.vercel, module.wristband_prod]
}

# Frontend .env files
resource "local_file" "frontend_env_dev" {
  count = var.wb_dev_application_vanity_domain != "" ? 1 : 0
  
  filename = "${path.module}/../frontend/.env.local"
  
  content = <<-EOT
NEXT_PUBLIC_APPLICATION_SIGNUP_URL=https://${var.wb_dev_application_vanity_domain}/signup
EOT

  file_permission = "0600"
}

resource "local_file" "frontend_env_staging" {
  count = var.deployment_enabled && var.wb_staging_application_vanity_domain != "" ? 1 : 0
  
  filename = "${path.module}/../frontend/.env.staging"
  
  content = <<-EOT
NEXT_PUBLIC_APPLICATION_SIGNUP_URL="https://${var.wb_staging_application_vanity_domain}/signup"
NEXT_PUBLIC_BACKEND_URL="${module.gcp[0].cloud_run_staging_url}"
VERCEL_ORG_ID="${var.vercel_org_id}"
VERCEL_PROJECT_ID="${module.vercel[0].vercel_project_id}"
VERCEL_PROJECT_NAME="${var.vercel_project_name}"
EOT

  file_permission = "0600"
  
  depends_on = [module.gcp, module.vercel, module.wristband_staging]
}

resource "local_file" "frontend_env_prod" {
  count = var.deployment_enabled && var.wb_prod_application_vanity_domain != "" ? 1 : 0
  
  filename = "${path.module}/../frontend/.env.prod"
  
  content = <<-EOT
NEXT_PUBLIC_APPLICATION_SIGNUP_URL="https://${var.wb_prod_application_vanity_domain}/signup"
NEXT_PUBLIC_BACKEND_URL="${module.gcp[0].cloud_run_prod_url}"
VERCEL_ORG_ID="${var.vercel_org_id}"
VERCEL_PROJECT_ID="${module.vercel[0].vercel_project_id}"
VERCEL_PROJECT_NAME="${var.vercel_project_name}"
EOT

  file_permission = "0600"
  
  depends_on = [module.gcp, module.vercel, module.wristband_prod]
}

