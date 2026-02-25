from pydantic import BaseModel


class SecretConfig(BaseModel):
    """API input model for creating/updating a secret.

    Contains the plaintext token which will be encrypted by the service.
    """
    name: str
    displayName: str
    environmentId: str
    token: str


class SecretResponse(BaseModel):
    """API response model for secrets.

    Contains the decrypted token for client consumption.
    """
    name: str
    displayName: str
    environmentId: str
    token: str


class SecretExistsResponse(BaseModel):
    """Response model for checking if a secret exists."""
    exists: bool
