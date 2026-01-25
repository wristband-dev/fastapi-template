terraform {
  required_providers {
    stripe = {
      source  = "lukasaron/stripe"
      version = "~> 2.0"
    }
  }
}

resource "stripe_product" "main" {
  name        = var.product_name
  description = "Access to ${var.product_name}"
}

# Pro Plan ($150/month)
resource "stripe_price" "pro" {
  product     = stripe_product.main.id
  currency    = "usd"
  unit_amount = 15000 # $150.00
  recurring {
    interval       = "month"
    interval_count = 1
  }
  nickname    = "Pro Plan"
}

# Customer Portal Configuration
resource "stripe_portal_configuration" "main" {
  business_profile {
    headline = "Manage your subscription"
  }
  features {
    customer_update {
      enabled         = true
      allowed_updates = ["email", "address", "phone"]
    }
    invoice_history {
      enabled = true
    }
    payment_method_update {
      enabled = true
    }
    subscription_cancel {
      enabled = true
      mode    = "at_period_end"
    }
  }
}

# Webhook Endpoint (Only created if URL is provided)
resource "stripe_webhook_endpoint" "main" {
  count = var.webhook_url != "" ? 1 : 0

  url = "${var.webhook_url}/api/billing/webhook"
  enabled_events = [
    "checkout.session.completed",
    "customer.subscription.updated",
    "customer.subscription.deleted"
  ]
}
