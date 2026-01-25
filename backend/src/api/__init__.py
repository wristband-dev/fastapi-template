from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Local imports
from api.endpoints import auth_api
from api.endpoints import user_api
from api.endpoints import users_api
from api.endpoints import roles_api
from api.endpoints import tenant_api
from api.endpoints import idp_api
from api.endpoints import secrets_api
from api.endpoints import billing_api
# Create main API router
router = APIRouter()

# Include endpoint routers
router.include_router(auth_api.router, prefix="/api/auth", tags=["auth"])
router.include_router(user_api.router, prefix="/api/user", tags=["user"])
router.include_router(users_api.router, prefix="/api/users", tags=["users"])
router.include_router(roles_api.router, prefix="/api/roles", tags=["roles"])
router.include_router(tenant_api.router, prefix="/api/tenant", tags=["tenant"])
router.include_router(idp_api.router, prefix="/api/idp", tags=["idp"])
router.include_router(secrets_api.router, prefix="/api/secrets", tags=["secrets"])
router.include_router(billing_api.router, prefix="/api/billing", tags=["billing"])

# Add root endpoint
@router.get("/")
async def root():
    return JSONResponse({
        "message": "API",
        "status": "running",
    })