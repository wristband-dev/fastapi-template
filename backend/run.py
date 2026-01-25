# Standard library imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

# Load environment variables BEFORE local imports
from environment import environment as env

# Local imports
from wristband.fastapi_auth import SessionMiddleware, SameSiteOption
from api import router

def create_app() -> FastAPI:
    app = FastAPI()

    # Set up logging
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
    
    # Suppress noisy Wristband auth errors for expired tokens (expected behavior)
    # These errors occur when refresh tokens expire, which is normal and handled by redirect to login
    logging.getLogger("wristband.fastapi_auth.auth").setLevel(logging.CRITICAL)
    # Also suppress httpx INFO logs about 400 responses during token refresh
    logging.getLogger("httpx").setLevel(logging.WARNING)

    ########################################################################################
    # IMPORTANT: FastAPI middleware runs in reverse order of the way it is added below!!
    ########################################################################################

    # Add session middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key="a8f5f167f44f4964e6c998dee827110c",
        secure=env.is_deployed,  # Only secure cookies in deployment (HTTPS)
        same_site=SameSiteOption.LAX,
        enable_csrf_protection=True,
    )

    # Add CORS middleware
    allowed_origins = [
        f"{env.frontend_url}",
    ]

    if env.is_deployed:
        allowed_origins.append(f"{env.frontend_url}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Include API routers
    app.include_router(router)

    return app

# This app instance is used when imported by Uvicorn
app = create_app()

if __name__ == '__main__':
    # For Cloud Run, we need to bind to 0.0.0.0 and use the PORT environment variable
    is_deployed = env.is_deployed
    host = "0.0.0.0" if is_deployed else "localhost"
    port = 8080 if is_deployed else 6001
    
    uvicorn.run("run:app", host=host, port=port, reload=not is_deployed)
