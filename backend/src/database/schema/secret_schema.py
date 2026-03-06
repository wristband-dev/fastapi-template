from typing import Optional
from sqlmodel import Field

from database.schema import DatabaseModel, DBMixin, ResponseDatabaseModel


class SecretCreate(DatabaseModel):
    """Input fields for creating a secret."""

    name: str = Field(index=True)
    display_name: str
    environment_id: str
    encrypted_token: str
    tenant_id: str = Field(index=True, description="Owning tenant ID")


class SecretDB(SecretCreate, DBMixin, table=True):
    """Database table model."""

    __tablename__ = "secrets"

    id: Optional[int] = Field(default=None, primary_key=True)


class Secret(SecretCreate, ResponseDatabaseModel):
    """Response model with CRUD operations.

    Usage:
        Secret.find(name="my-secret", tenant_id="abc")
        Secret.query(tenant_id="abc")
        Secret.create(SecretCreate(...))
        Secret.delete(name="my-secret", tenant_id="abc")
    """

    __db_model__ = SecretDB

    id: int
