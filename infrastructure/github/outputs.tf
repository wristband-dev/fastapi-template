output "repository_name" {
  description = "GitHub repository name"
  value       = var.repository_name
}

output "secrets_uploaded" {
  description = "Summary of uploaded secrets"
  value = {
    repository_secrets = "10 secrets uploaded (Cloud Run, Vercel x4, GCP config x4)"
    staging_secrets    = "7 environment secrets uploaded"
    prod_secrets       = "7 environment secrets uploaded"
    total              = "24 secrets uploaded"
  }
}

