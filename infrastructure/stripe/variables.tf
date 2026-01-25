variable "product_name" {
  description = "Name of the product in Stripe"
  type        = string
  default     = "App Subscription"
}

variable "webhook_url" {
  description = "Public URL for the webhook endpoint (e.g. https://api.example.com). Leave empty to skip webhook creation."
  type        = string
  default     = ""
}
