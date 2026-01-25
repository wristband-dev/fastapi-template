# Models for secrets management
from pydantic import BaseModel
from typing import Self

from models import BaseDatabaseModel


class Secret(BaseDatabaseModel):
    """
    Database model for stored secrets.
    
    This is the encrypted form stored in the database.
    Tokens are encrypted before storage and decrypted on retrieval.
    """
    name: str
    displayName: str
    environmentId: str
    encryptedToken: str

    @classmethod
    def from_db(cls, data: dict) -> Self:
        """Create a Secret from database data"""
        return cls(**data)


class SecretConfig(BaseModel):
    """
    API input model for creating/updating a secret.
    
    Contains the plaintext token which will be encrypted by the store.
    """
    name: str
    displayName: str
    environmentId: str
    token: str


class SecretResponse(BaseModel):
    """
    API response model for secrets.
    
    Contains the decrypted token for client consumption.
    """
    name: str
    displayName: str
    environmentId: str
    token: str


class SecretExistsResponse(BaseModel):
    """Response model for checking if a secret exists"""
    exists: bool
