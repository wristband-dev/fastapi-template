from pydantic import Field

from models import BaseDatabaseModel


class Customer(BaseDatabaseModel):
    """Represents a customer in the system - maps Wristband tenant to Stripe customer"""
    id: str  # Stripe Customer ID
    metadata: dict = Field(default_factory=dict)
    tenant_id: str = Field(..., description="The Tenant ID associated with this customer")
    email: str = Field(..., description="The email of the customer")
