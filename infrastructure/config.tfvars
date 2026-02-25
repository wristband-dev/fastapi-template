# Infrastructure Configuration (Non-Sensitive - Tracked in Git)
# Sensitive values are in secrets.tfvars (gitignored)
# Run: terraform apply -var-file="config.tfvars" -var-file="secrets.tfvars"

# ═══════════════════════════════════════════════════════════════════════════════
#  DEPLOYMENT CONTROL
# ═══════════════════════════════════════════════════════════════════════════════

deploy_cloud_infrastructure = true

# ═══════════════════════════════════════════════════════════════════════════════
#  BRANDING (Optional)
# ═══════════════════════════════════════════════════════════════════════════════

# color: Button backgrounds/borders (with white text for contrast)
# logo_url: Displayed on login pages and in email headers
logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Logo_of_YouTube_%282015-2017%29.svg/960px-Logo_of_YouTube_%282015-2017%29.svg.png"
color    = "#FF0000"

# ═══════════════════════════════════════════════════════════════════════════════
#  WRISTBAND AUTHENTICATION (vanity domains are non-sensitive)
# ═══════════════════════════════════════════════════════════════════════════════

wb_dev_application_vanity_domain     = "dev-fastapitemplate.us.wristband.dev"
wb_staging_application_vanity_domain = "staging-fastapitemplate.us.wristband.dev"
wb_prod_application_vanity_domain    = "prod-fastapitemplate.us.wristband.dev"

# ═══════════════════════════════════════════════════════════════════════════════
#  GOOGLE CLOUD PLATFORM (requires deploy_cloud_infrastructure = true)
# ═══════════════════════════════════════════════════════════════════════════════

gcp_project_id             = "fastapi-template-test-022426"
gcp_region                 = "us-central1"
gcp_app_name               = "Fast API Template"
gcp_api_name               = "api"
gcp_api_repo_name          = "api-repo"
gcp_db_tier                = "db-f1-micro"
gcp_db_version             = "POSTGRES_16"
gcp_db_deletion_protection = true
gcp_db_iam_users           = []

# ═══════════════════════════════════════════════════════════════════════════════
#  VERCEL FRONTEND (requires deploy_cloud_infrastructure = true)
# ═══════════════════════════════════════════════════════════════════════════════

vercel_project_name = "fastapi-template"
vercel_domain_name  = ""

# ═══════════════════════════════════════════════════════════════════════════════
#  GITHUB (non-sensitive)
# ═══════════════════════════════════════════════════════════════════════════════

github_repository = "https://github.com/wristband-dev/fastapi-template"
