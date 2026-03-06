from typing import Optional
from sqlmodel import Field

from database.schema import DatabaseModel, DBMixin, ResponseDatabaseModel


class CustomerCreate(DatabaseModel):
    """Input fields for creating a customer."""

    stripe_id: str = Field(index=True, description="Stripe Customer ID")
    tenant_id: str = Field(index=True, description="Wristband Tenant ID")
    email: str = Field(description="Customer email")
    metadata_json: str = Field(default="{}", description="JSON metadata blob")


class CustomerDB(CustomerCreate, DBMixin, table=True):
    """Database table model."""

    __tablename__ = "customers"

    id: Optional[int] = Field(default=None, primary_key=True)


class Customer(CustomerCreate, ResponseDatabaseModel):
    """Response model with CRUD operations.

    Usage:
        Customer.get(42)
        Customer.find(tenant_id="abc")
        Customer.query(tenant_id="abc")
        Customer.create(CustomerCreate(...))
        Customer.update(42, email="new@email.com")
    """

    __db_model__ = CustomerDB

    id: int
