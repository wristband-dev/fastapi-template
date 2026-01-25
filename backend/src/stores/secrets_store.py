import logging
from typing import List, Optional

from stores.base import BaseStore
from models.wristband.session import MySession
from models.secrets import Secret, SecretConfig, SecretResponse
from services.encryption_service import encrypt_secret, decrypt_secret

logger = logging.getLogger(__name__)

SECRETS_COLLECTION = "secrets"


class SecretsStore(BaseStore[Secret]):
    """
    Store for encrypted secrets.
    
    Secrets are stored with tenant scoping - each tenant has their own
    isolated set of secrets.
    
    This store handles encryption/decryption of secret tokens:
    - Input: SecretConfig (with plaintext token)
    - Storage: Secret (with encrypted token)
    - Output: SecretResponse (with decrypted token)
    """

    def __init__(self, session: MySession):
        super().__init__(
            session, 
            SECRETS_COLLECTION, 
            Secret,
            use_tenant_scope=True  # Secrets are tenant-scoped
        )

    def save_secret(self, config: SecretConfig) -> str:
        """
        Save a secret, encrypting the token before storage.
        
        Args:
            config: The secret configuration with plaintext token
            
        Returns:
            The document ID of the saved secret
        """
        # Encrypt and create storage model
        secret = Secret(
            name=config.name,
            displayName=config.displayName,
            environmentId=config.environmentId,
            encryptedToken=encrypt_secret(config.token)
        )
        
        # Use the secret name as the document ID
        return self.set(config.name, secret)

    def get_secret(self, name: str) -> Optional[SecretResponse]:
        """
        Get a secret by name, decrypting the token.
        
        Args:
            name: The name of the secret
            
        Returns:
            SecretResponse with decrypted token, or None if not found
        """
        secret = self.get_or_none(name)
        if secret is None:
            return None
        
        return self._decrypt_secret(secret)

    def get_all_secrets(self) -> List[SecretResponse]:
        """
        Get all secrets for the tenant, decrypting all tokens.
        
        Returns:
            List of SecretResponse with decrypted tokens
        """
        secrets = self.get_all()
        return [self._decrypt_secret(secret) for secret in secrets]

    def _decrypt_secret(self, secret: Secret) -> SecretResponse:
        """Convert a stored Secret to a SecretResponse with decrypted token."""
        try:
            decrypted_token = decrypt_secret(secret.encryptedToken)
            return SecretResponse(
                name=secret.name,
                displayName=secret.displayName,
                environmentId=secret.environmentId,
                token=decrypted_token
            )
        except Exception as e:
            error_message = f"Failed to decrypt secret {secret.name}: {str(e)}"
            logger.error(error_message)
            raise ValueError(error_message)
