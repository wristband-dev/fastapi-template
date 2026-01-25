# Standard library imports
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.responses import Response

# Wristband imports
from wristband.fastapi_auth import SessionResponse

# Local imports
from services.wristband_service import get_wristband_service, WristbandService
from auth.wristband import require_session_auth


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/login')
async def login(svc: WristbandService = Depends(get_wristband_service)) -> Response:
    return await svc.login()

@router.get('/callback')
async def callback(svc: WristbandService = Depends(get_wristband_service)) -> Response:
    return await svc.callback()

@router.get('/logout')
async def logout(svc: WristbandService = Depends(get_wristband_service)) -> Response:
    return await svc.logout()

@router.get("/session", dependencies=[Depends(require_session_auth)])
async def get_session(
    response: Response,
    svc: WristbandService = Depends(get_wristband_service)
) -> SessionResponse:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    try:
        return await svc.get_session()
    except Exception as e:
        logger.exception(f"Unexpected Get Session Endpoint error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
