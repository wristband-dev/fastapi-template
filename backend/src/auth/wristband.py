import os

from wristband.fastapi_auth import AuthConfig, WristbandAuth
from environment import environment as env

# Explicitly define what can be imported
__all__ = ["require_session_auth", "wristband_auth"]

wristband_auth: WristbandAuth = WristbandAuth(
    AuthConfig(
        client_id=env.client_id,
        client_secret=env.client_secret,
        wristband_application_vanity_domain=env.application_vanity_domain,
        scopes=["openid", "offline_access", "email", "profile", "roles"],
        dangerously_disable_secure_cookies=not env.is_deployed
    )
)

require_session_auth = wristband_auth.create_session_auth_dependency(
    enable_csrf_protection=True,
    csrf_header_name="X-CSRF-TOKEN"
)