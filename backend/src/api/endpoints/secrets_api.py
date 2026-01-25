# Standard library imports
import logging
from fastapi import APIRouter, Depends
from typing import List

# Local imports
from auth.wristband import require_session_auth
from services.secrets_service import get_secrets_service, SecretsService
from models.secrets import SecretConfig, SecretResponse, SecretExistsResponse

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_session_auth)])


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get('', response_model=List[SecretResponse])
async def get_secrets(svc: SecretsService = Depends(get_secrets_service)):
    """Get all secrets"""
    return await svc.get_secrets()


@router.post('/upsert')
async def upsert_secret(
    secret: SecretConfig,
    svc: SecretsService = Depends(get_secrets_service)
):
    """Create or update a secret"""
    return await svc.upsert_secret(secret)


@router.get('/check/{name}', response_model=SecretExistsResponse)
async def check_secret_exists(
    name: str,
    svc: SecretsService = Depends(get_secrets_service)
):
    """Check if a secret with the given name exists"""
    return await svc.check_secret_exists(name)


@router.delete('/{name}')
async def delete_secret(
    name: str,
    svc: SecretsService = Depends(get_secrets_service)
):
    """Delete a secret"""
    return await svc.delete_secret(name)
