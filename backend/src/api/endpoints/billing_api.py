import logging
from typing import Optional
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from auth.wristband import require_session_auth
from services.stripe_service import get_stripe_service, StripeService, StripeProducts
from models.stripe import StripeSubscription

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_session_auth)])


@router.get("/products", response_model=StripeProducts)
async def get_products(
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Get all available Stripe products and their prices.
    """
    try:
        products = await stripe_svc.get_products()
        return products
    except Exception as e:
        logger.exception(f"Error fetching products: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while fetching products."}
        )


@router.post("/checkout", status_code=status.HTTP_200_OK)
async def create_checkout_session(
    price_id: str,
    billing_email: Optional[str] = None,
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Create a Stripe Checkout session for upgrading to a paid plan.

    Args:
        price_id: The Stripe price ID for the plan
        billing_email: Optional alternate email for billing (overrides user's email)
    """
    try:
        checkout_url = await stripe_svc.create_checkout_session(
            price_id=price_id,
            billing_email=billing_email,
        )
        return {"url": checkout_url}
    except Exception as e:
        logger.exception(f"Error creating checkout session: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while creating checkout session."}
        )


@router.get("/subscription", response_model=Optional[StripeSubscription])
async def get_active_subscription(
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Get the active Stripe subscription for the current tenant.
    Returns null if no active subscription exists.
    """
    try:
        subscription = await stripe_svc.get_active_subscription()
        return subscription
    except Exception as e:
        logger.exception(f"Error fetching subscription: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while fetching subscription."}
        )


@router.put("/subscriptions/{subscription_id}", response_model=StripeSubscription)
async def update_subscription(
    subscription_id: str,
    new_price_id: str,
    billing_email: Optional[str] = None,
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Update an existing subscription to a new plan.

    Handles proration automatically:
    - Upgrading: Charges the price difference immediately
    - Downgrading: Credits the difference to the next invoice

    Args:
        subscription_id: The Stripe subscription ID to update
        new_price_id: The new Stripe price ID to switch to
        billing_email: Optional new billing email (updates customer record)
    """
    try:
        updated_subscription = await stripe_svc.update_subscription(
            subscription_id=subscription_id,
            new_price_id=new_price_id,
            billing_email=billing_email,
        )
        return updated_subscription
    except Exception as e:
        logger.exception(f"Error updating subscription: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while updating subscription."}
        )


@router.post("/portal", status_code=status.HTTP_200_OK)
async def create_portal_session(
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Create a Stripe Customer Portal session.

    The portal allows customers to:
    - Update payment methods
    - View invoice history
    - Update billing information

    Returns a URL to redirect the user to the Stripe Customer Portal.
    """
    try:
        portal_url = await stripe_svc.create_portal_session()
        return {"url": portal_url}
    except Exception as e:
        logger.exception(f"Error creating portal session: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while creating portal session."}
        )


# =============================================================================
# BILLING INFO ENDPOINTS
# =============================================================================

@router.get("/billing-info", status_code=status.HTTP_200_OK)
async def get_billing_info(
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Get billing information for the current tenant.
    
    Returns:
        billing_email: The email used for billing
        has_payment_method: Whether a payment method is on file
    """
    try:
        billing_info = await stripe_svc.get_billing_info()
        return billing_info
    except Exception as e:
        logger.exception(f"Error fetching billing info: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while fetching billing info."}
        )


@router.put("/billing-email", status_code=status.HTTP_200_OK)
async def update_billing_email(
    email: str,
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Update the billing email for the current tenant's customer.
    
    Args:
        email: The new billing email address
    """
    try:
        result = await stripe_svc.update_billing_email(email)
        return result
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "bad_request", "message": str(e)}
        )
    except Exception as e:
        logger.exception(f"Error updating billing email: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while updating billing email."}
        )


# =============================================================================
# USAGE-BASED BILLING ENDPOINTS
# =============================================================================

@router.post("/usage", status_code=status.HTTP_200_OK)
async def add_usage(
    amount: int,
    description: str = "Usage charge",
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Add a usage charge to the customer's account.
    The charge will be added to the next invoice.
    
    Args:
        amount: Amount in cents (e.g., 1000 = $10.00)
        description: Description for the charge
    """
    try:
        result = await stripe_svc.add_usage(amount, description)
        return result
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "bad_request", "message": str(e)}
        )
    except Exception as e:
        logger.exception(f"Error adding usage: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while adding usage."}
        )


@router.get("/usage", status_code=status.HTTP_200_OK)
async def get_pending_usage(
    stripe_svc: StripeService = Depends(get_stripe_service),
):
    """
    Get pending usage charges for the current tenant.
    These are charges that haven't been invoiced yet.
    """
    try:
        usage = await stripe_svc.get_pending_usage()
        return usage
    except Exception as e:
        logger.exception(f"Error fetching pending usage: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred while fetching pending usage."}
        )
