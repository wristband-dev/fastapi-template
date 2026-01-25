import logging
import stripe
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends

from wristband.fastapi_auth import get_session
from environment import environment
from models.wristband.session import MySession
from models.stripe import (
    StripeProduct,
    StripeProducts,
    StripeSubscription,
    PriceInterval,
    SubscriptionStatus,
)
from stores.customer_store import CustomerStore
from models.customer import Customer


logger = logging.getLogger(__name__)

# =============================================================================
# BILLING CONFIGURATION CONSTANTS
# =============================================================================
FREE_TRIAL_DURATION_DAYS: int | None = 1  # Set to None to disable auto-cancel after trial
DEFAULT_CURRENCY: str = "usd"


def get_tenant_id(session: MySession) -> Optional[str]:
    """Get tenant ID from session"""
    return session.tenant_id


def get_tenant_name(session: MySession) -> Optional[str]:
    """Get tenant name from session"""
    return session.tenant_name


def get_stripe_service(
    session: MySession = Depends(get_session)
) -> "StripeService":
    return StripeService(session)


class StripeService:
    def __init__(self, session: MySession):
        self.api_key: str = environment.get_stripe_secret_key()
        stripe.api_key = self.api_key

        self.session: MySession = session
        self.customer_store = CustomerStore(session)

    async def ensure_customer(self, billing_email: Optional[str] = None) -> str:
        """
        Ensure a Stripe customer exists for the current tenant.
        Creates customer + free trial subscription if new.
        """
        tenant_name = get_tenant_name(self.session)
        tenant_id = get_tenant_id(self.session)

        email = billing_email or self.session.email
        if email is None or tenant_name is None or tenant_id is None:
            raise ValueError("Email and tenant_name and tenant_id are required")

        # 1. Find existing customer ID for this tenant
        customer_id = None
        customers = self.customer_store.get_by_field("tenant_id", tenant_id)
        if customers:
            customer_id = customers[0].id
            logger.info(f"Found existing Stripe customer for tenant {tenant_name}: {customer_id}")
            # 1.a. Update customer email if it differs (billing_email override)
            if billing_email is not None and customers[0].email != billing_email:
                logger.info(f"Updating Stripe customer email for tenant {tenant_name}: {email}")
                stripe_customer = stripe.Customer.modify(customer_id, email=email)
                self.customer_store.update(customer_id, Customer(
                    id=stripe_customer.id,
                    email=email,
                    tenant_id=tenant_id,
                ))
                customer_id = stripe_customer.id
            return customer_id

        # 2. Create new customer
        logger.info(f"Creating Stripe customer for tenant {tenant_name}")
        stripe_customer = stripe.Customer.create(
            email=email,
            name=tenant_name,
            metadata={"tenant_id": tenant_id, "tenant_name": tenant_name},
        )
        customer_id = stripe_customer.id

        self.customer_store.add(Customer(
            id=stripe_customer.id,
            tenant_id=tenant_id,
            email=email,
        ))

        # 2.a. Create a trial subscription with the Pro price (if trial is enabled)
        if FREE_TRIAL_DURATION_DAYS is not None and FREE_TRIAL_DURATION_DAYS > 0:
            pro_products = await self.get_products()
            if not pro_products:
                raise ValueError("No paid products available for trial subscription")
            pro_price_id = pro_products[0].price_id
            trial_end = int((datetime.now() + timedelta(days=FREE_TRIAL_DURATION_DAYS)).timestamp())

            logger.info(f"Creating trial subscription for customer {customer_id}")
            stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": pro_price_id}],
                trial_end=trial_end,
                trial_settings={"end_behavior": {"missing_payment_method": "cancel"}},
                metadata={"tenant_id": tenant_id, "type": "trial"},
            )
            logger.info(f"Trial subscription created, trial ends at {trial_end}")
        else:
            # No trial - customer must subscribe to access
            logger.info(f"Trial disabled, customer {customer_id} must subscribe to access")

        return customer_id

    async def create_checkout_session(self, price_id: str, billing_email: Optional[str] = None) -> str:
        """Create a Stripe Checkout session for upgrading to a paid plan."""
        tenant_id = get_tenant_id(self.session)
        tenant_name = get_tenant_name(self.session)

        customer_id = await self.ensure_customer(billing_email)

        success_url = f"{environment.frontend_url}/billing?success=true"
        cancel_url = f"{environment.frontend_url}/billing?canceled=true"

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"tenant_id": tenant_id, "tenant_name": tenant_name},
            subscription_data={
                "metadata": {"tenant_id": tenant_id, "tenant_name": tenant_name}
            }
        )

        if not checkout_session.url:
            raise ValueError("Failed to create checkout session URL")

        return checkout_session.url

    async def get_products(self) -> StripeProducts:
        """
        Fetch all active paid products with their prices from Stripe.
        Returns products that have at least one active price with amount > 0.
        """
        products_list: StripeProducts = []

        # Fetch all active prices with their associated products expanded
        prices = stripe.Price.list(
            active=True,
            expand=["data.product"],
            limit=100
        )

        for price in prices.data:
            product = price.product

            # Skip if product is not active or is deleted
            if isinstance(product, str):
                continue
            if not product.active:
                continue

            # Get price details
            price_amount = price.unit_amount or 0
            price_currency = price.currency
            price_interval = None
            if price.recurring and price.recurring.interval:
                price_interval = PriceInterval(price.recurring.interval)

            # Only include paid products (skip $0 prices if any exist)
            if price_amount == 0:
                continue

            products_list.append(StripeProduct(
                id=product.id,
                name=product.name,
                description=product.description,
                price_id=price.id,
                price_amount=price_amount,
                price_currency=price_currency,
                price_interval=price_interval
            ))

        return products_list

    async def get_active_subscription(self) -> Optional[StripeSubscription]:
        """
        Get the active subscription for the current tenant's customer.
        Returns the subscription with status 'active' or 'trialing', or None if none exists.

        If no customer exists, automatically creates one with a trial subscription.
        If multiple subscriptions exist (e.g., trial + new paid), automatically
        cancels the trial one(s) and returns the paid subscription.
        """
        tenant_id = get_tenant_id(self.session)

        # Find customer for this tenant
        customers = self.customer_store.get_by_field("tenant_id", tenant_id)
        if not customers:
            # No customer exists - create one with trial subscription
            logger.info(f"No customer found for tenant {tenant_id}, creating with trial subscription")
            await self.ensure_customer()
            # Re-fetch customer after creation
            customers = self.customer_store.get_by_field("tenant_id", tenant_id)
            if not customers:
                logger.warning(f"Failed to create customer for tenant {tenant_id}")
                return None

        customer_id = customers[0].id

        # Fetch ALL active subscriptions from Stripe
        active_subs = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            expand=["data.items.data.price"],
            limit=10
        )

        # Also fetch trialing subscriptions
        trialing_subs = stripe.Subscription.list(
            customer=customer_id,
            status="trialing",
            expand=["data.items.data.price"],
            limit=10
        )

        # Combine all subscriptions
        all_subs = list(active_subs.data) + list(trialing_subs.data)

        if not all_subs:
            return None

        # If multiple subscriptions exist, clean up: cancel free ones, keep paid
        if len(all_subs) > 1:
            all_subs = self._cleanup_duplicate_subscriptions(all_subs)

        # Get the subscription to return (should be only one now, prefer paid)
        sub = all_subs[0]

        return self._subscription_to_model(sub)

    def _cleanup_duplicate_subscriptions(self, subscriptions: list) -> list:
        """
        When multiple subscriptions exist, cancel trialing ones and keep active ones.
        Returns the list of remaining subscriptions after cleanup.
        """
        trialing_subs = []
        active_subs = []

        for sub in subscriptions:
            status = sub.get("status") if isinstance(sub, dict) else sub.status
            if status == "trialing":
                trialing_subs.append(sub)
            else:
                active_subs.append(sub)

        # If we have active (paid) subscriptions, cancel the trialing ones
        if active_subs and trialing_subs:
            for trial_sub in trialing_subs:
                sub_id = trial_sub.get("id") if isinstance(trial_sub, dict) else trial_sub.id
                try:
                    logger.info(f"Cleaning up duplicate subscription: canceling trial subscription {sub_id}")
                    stripe.Subscription.cancel(sub_id)
                except stripe.InvalidRequestError as e:
                    logger.warning(f"Could not cancel trial subscription {sub_id}: {e}")
            return active_subs

        # If only trialing subs or only active subs, return all
        return subscriptions

    def _subscription_to_model(self, sub) -> StripeSubscription:
        """
        Convert a Stripe subscription object to our StripeSubscription model.
        """
        # Get the first item (most subscriptions have one item)
        items_data = sub["items"]["data"]
        if not items_data:
            raise ValueError("Subscription has no items")

        item = items_data[0]
        price = item["price"]

        # Get product info
        product = price.get("product") if isinstance(price, dict) else price.product
        if isinstance(product, str):
            try:
                product_obj = stripe.Product.retrieve(product)
                product_id = product
                product_name = product_obj.name
                product_description = product_obj.description
            except Exception:
                product_id = product
                product_name = "Unknown"
                product_description = None
        elif isinstance(product, dict):
            product_id = str(product.get("id", "unknown"))
            product_name = str(product.get("name", "Unknown"))
            product_description = product.get("description")
        else:
            product_id = str(product.id) if product else "unknown"
            product_name = str(product.name) if product else "Unknown"
            product_description = product.description if product else None

        # Get price interval
        recurring = price.get("recurring") if isinstance(price, dict) else price.recurring
        price_interval = None
        if recurring:
            interval = recurring.get("interval") if isinstance(recurring, dict) else recurring.interval
            if interval:
                price_interval = PriceInterval(interval)

        # Get price fields with dict-style access
        price_id_val = str(price.get("id", "")) if isinstance(price, dict) else str(price.id)
        price_amount_val = int(price.get("unit_amount", 0) or 0) if isinstance(price, dict) else (price.unit_amount or 0)
        price_currency_val = str(price.get("currency", DEFAULT_CURRENCY)) if isinstance(price, dict) else str(price.currency)

        # Get period from subscription item
        current_period_start = item.get("current_period_start", 0) if isinstance(item, dict) else item.current_period_start
        current_period_end = item.get("current_period_end", 0) if isinstance(item, dict) else item.current_period_end

        return StripeSubscription(
            id=sub.id,
            status=SubscriptionStatus(sub.status),
            current_period_start=int(current_period_start or 0),
            current_period_end=int(current_period_end or 0),
            cancel_at_period_end=sub.cancel_at_period_end,
            cancel_at=int(sub.cancel_at) if sub.cancel_at else None,
            product_id=product_id,
            product_name=product_name,
            product_description=product_description,
            price_id=price_id_val,
            price_amount=price_amount_val,
            price_currency=price_currency_val,
            price_interval=price_interval
        )

    async def is_subscribed(self) -> bool:
        """
        Check if the current tenant has an active subscription.
        """
        subscription = await self.get_active_subscription()
        logger.info('subscription: %s', subscription)
        return subscription is not None and subscription.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING)

    async def is_free_period(self) -> bool:
        """
        Check if the current tenant is in a free trial period.
        """
        subscription = await self.get_active_subscription()
        return subscription is not None and subscription.status == SubscriptionStatus.TRIALING

    async def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str,
        billing_email: Optional[str] = None,
    ) -> StripeSubscription:
        """
        Update an existing subscription to a new price/plan.

        Handles proration automatically when changing between price tiers.
        """
        # Update customer billing email if provided
        if billing_email:
            await self.ensure_customer(billing_email)

        # Get the current subscription to find the subscription item
        subscription = stripe.Subscription.retrieve(subscription_id)

        if not subscription["items"]["data"]:
            raise ValueError("Subscription has no items")

        # Get the first subscription item
        subscription_item_id = subscription["items"]["data"][0]["id"]

        # Update the subscription with proration
        updated_sub = stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription_item_id,
                "price": new_price_id,
            }],
            proration_behavior="create_prorations",
        )

        return self._subscription_to_model(updated_sub)

    async def create_portal_session(self) -> str:
        """
        Create a Stripe Customer Portal session for the current tenant.
        The portal allows customers to manage their payment methods, view invoices,
        and update billing information.

        Returns:
            The URL to redirect the user to the Stripe Customer Portal
        """
        customer_id = await self.ensure_customer()

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{environment.frontend_url}/admin"
        )

        if not session.url:
            raise ValueError("Failed to create portal session URL")

        return session.url

    # =========================================================================
    # BILLING INFO METHODS
    # =========================================================================

    async def get_billing_info(self) -> dict:
        """
        Get billing info including customer email and payment method status.
        """
        tenant_id = get_tenant_id(self.session)
        customers = self.customer_store.get_by_field("tenant_id", tenant_id)
        
        if not customers:
            return {
                "billing_email": self.session.email,
                "has_payment_method": False
            }
        
        customer = stripe.Customer.retrieve(customers[0].id)
        has_payment = bool(
            customer.invoice_settings and 
            customer.invoice_settings.default_payment_method
        )
        
        return {
            "billing_email": customer.email,
            "has_payment_method": has_payment
        }

    async def update_billing_email(self, new_email: str) -> dict:
        """
        Update the billing email for the customer.
        """
        tenant_id = get_tenant_id(self.session)
        customers = self.customer_store.get_by_field("tenant_id", tenant_id)
        
        if not customers:
            raise ValueError("No customer found")
        
        customer_id = customers[0].id
        
        # Update in Stripe
        stripe.Customer.modify(customer_id, email=new_email)
        
        # Update in local store
        self.customer_store.update(customer_id, Customer(
            id=customer_id,
            email=new_email,
            tenant_id=tenant_id,
        ))
        
        logger.info(f"Updated billing email for customer {customer_id} to {new_email}")
        return {"billing_email": new_email}

    # =========================================================================
    # USAGE-BASED BILLING METHODS
    # =========================================================================

    async def add_usage(self, amount: int, description: str = "Usage charge") -> dict:
        """
        Add a usage charge to the customer's account.
        Creates an invoice item that will be added to the next invoice.
        
        Args:
            amount: Amount in cents (e.g., 1000 = $10.00)
            description: Description for the charge
        
        Returns:
            Dict with invoice item details
        """
        tenant_id = get_tenant_id(self.session)
        customers = self.customer_store.get_by_field("tenant_id", tenant_id)
        
        if not customers:
            raise ValueError("No customer found. Please set up billing first.")
        
        customer_id = customers[0].id
        
        # Create an invoice item for the usage
        invoice_item = stripe.InvoiceItem.create(
            customer=customer_id,
            amount=amount,
            currency=DEFAULT_CURRENCY,
            description=description,
        )
        
        logger.info(f"Created usage charge of {amount} cents for customer {customer_id}")
        
        return {
            "id": invoice_item.id,
            "amount": invoice_item.amount,
            "currency": invoice_item.currency,
            "description": invoice_item.description,
        }

    async def get_pending_usage(self) -> list:
        """
        Get pending invoice items (usage charges) for the customer.
        These are charges that haven't been invoiced yet.
        """
        tenant_id = get_tenant_id(self.session)
        customers = self.customer_store.get_by_field("tenant_id", tenant_id)
        
        if not customers:
            logger.warning(f"No customer found for tenant {tenant_id}")
            return []
        
        customer_id = customers[0].id
        logger.info(f"Fetching pending usage for customer {customer_id}")
        
        items = stripe.InvoiceItem.list(
            customer=customer_id,
            pending=True,
            limit=100
        )
        
        logger.info(f"Found {len(items.data)} pending invoice items")
        
        return [
            {
                "id": item.id,
                "amount": item.amount,
                "currency": item.currency,
                "description": item.description,
                "date": item.date,
            }
            for item in items.data
        ]
