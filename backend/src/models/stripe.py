from enum import Enum
from typing import Optional, TypeAlias, List
from pydantic import BaseModel


class PriceInterval(str, Enum):
    """Stripe price billing interval."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class SubscriptionStatus(str, Enum):
    """Stripe subscription status."""
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    TRIALING = "trialing"
    UNPAID = "unpaid"


class StripeProduct(BaseModel):
    """Represents a Stripe product with its associated price."""
    id: str
    name: str
    description: Optional[str] = None
    price_id: str
    price_amount: int  # Amount in cents
    price_currency: str
    price_interval: Optional[PriceInterval] = None


class StripeSubscription(BaseModel):
    """Represents a Stripe subscription."""
    id: str
    status: SubscriptionStatus
    current_period_start: int  # Unix timestamp
    current_period_end: int  # Unix timestamp
    cancel_at_period_end: bool
    cancel_at: Optional[int] = None  # Unix timestamp for scheduled cancellation
    product_id: str
    product_name: str
    product_description: Optional[str] = None
    price_id: str
    price_amount: int  # Amount in cents
    price_currency: str
    price_interval: Optional[PriceInterval] = None


StripeProducts: TypeAlias = List[StripeProduct]
StripeSubscriptions: TypeAlias = List[StripeSubscription]
