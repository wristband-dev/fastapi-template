import logging
from typing import List
from fastapi import Depends, status, Request
from fastapi.responses import JSONResponse

from wristband.fastapi_auth import get_session

from services.encryption_service import encrypt_secret, decrypt_secret, get_encryption_service
from models.wristband.session import MySession
from database.schema.secret_schema import Secret, SecretCreate
from models.secrets import SecretConfig, SecretResponse, SecretExistsResponse

logger = logging.getLogger(__name__)


# MARK: - Dependencies
def get_secrets_service(
    request: Request,
    session: MySession = Depends(get_session)
) -> 'SecretsService':
    return SecretsService(request, session)


# MARK: - Service
class SecretsService:
    def __init__(self, request: Request, session: MySession):
        self.encryption_svc = get_encryption_service()
        self.session = session
        self.tenant_id = session.tenant_id or ""

    def _check_encryption_available(self):
        if not self.encryption_svc.is_available():
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"error": "encryption_unavailable", "message": "Encryption service is not available"}
            )
        return None

    def _decrypt_to_response(self, secret: Secret) -> SecretResponse:
        """Decrypt a Secret model into a SecretResponse for the API."""
        try:
            decrypted_token = decrypt_secret(secret.encrypted_token)
            return SecretResponse(
                name=secret.name,
                displayName=secret.display_name,
                environmentId=secret.environment_id,
                token=decrypted_token,
            )
        except Exception as e:
            error_message = f"Failed to decrypt secret {secret.name}: {str(e)}"
            logger.error(error_message)
            raise ValueError(error_message)

    async def get_secrets(self) -> List[SecretResponse] | JSONResponse:
        try:
            if error := self._check_encryption_available():
                return error

            secrets = Secret.query(tenant_id=self.tenant_id)
            return [self._decrypt_to_response(s) for s in secrets]

        except Exception as e:
            logger.exception(f"Error fetching secrets: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "internal_error", "message": "Failed to fetch secrets"}
            )

    async def upsert_secret(self, secret: SecretConfig) -> JSONResponse:
        try:
            if error := self._check_encryption_available():
                return error

            try:
                existing = Secret.find(name=secret.name, tenant_id=self.tenant_id)
                encrypted_token = encrypt_secret(secret.token)

                if existing:
                    Secret.update(
                        existing.id,
                        display_name=secret.displayName,
                        environment_id=secret.environmentId,
                        encrypted_token=encrypted_token,
                    )
                else:
                    Secret.create(SecretCreate(
                        name=secret.name,
                        display_name=secret.displayName,
                        environment_id=secret.environmentId,
                        encrypted_token=encrypted_token,
                        tenant_id=self.tenant_id,
                    ))
            except Exception as e:
                logger.error(f"Failed to encrypt token: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"error": "encryption_error", "message": "Failed to encrypt secret"}
                )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Secret saved successfully"}
            )

        except Exception as e:
            logger.exception(f"Error saving secret: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "internal_error", "message": "Failed to save secret"}
            )

    async def check_secret_exists(self, name: str) -> SecretExistsResponse | JSONResponse:
        try:
            exists = Secret.find(name=name, tenant_id=self.tenant_id) is not None
            return SecretExistsResponse(exists=exists)

        except Exception as e:
            logger.exception(f"Error checking secret existence: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "internal_error", "message": "Failed to check secret"}
            )

    async def delete_secret(self, name: str) -> JSONResponse:
        try:
            existing = Secret.find(name=name, tenant_id=self.tenant_id)
            if not existing:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": "not_found", "message": "Secret not found"}
                )

            Secret.delete(name=name, tenant_id=self.tenant_id)

            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT,
                content=None
            )

        except Exception as e:
            logger.exception(f"Error deleting secret: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "internal_error", "message": "Failed to delete secret"}
            )
