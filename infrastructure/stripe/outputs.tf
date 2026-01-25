output "product_id" {
  value = stripe_product.main.id
}

output "price_id_pro" {
  value = stripe_price.pro.id
}

output "webhook_secret" {
  value     = length(stripe_webhook_endpoint.main) > 0 ? stripe_webhook_endpoint.main[0].secret : ""
  sensitive = true
}

output "portal_configuration_id" {
  value = stripe_portal_configuration.main.id
}
