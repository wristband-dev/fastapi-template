# Standard library imports
from fastapi import Depends, Request, Response
import logging

# Wristband imports
from wristband.fastapi_auth import (
  get_session,
  CallbackResult,
  CompletedCallbackResult,
  RedirectRequiredCallbackResult,
  LogoutConfig,
  SessionResponse,
)

# Local imports
from environment import environment as env
from auth.wristband import wristband_auth
from clients.wristband_client import WristbandClient
from models.wristband.session import MySession
from models.wristband.user import (
    User, 
    UpdateNameRequest, 
    PasswordChangeRequest,
)
from models.wristband.role import Role
from models.wristband.invite import NewUserInvitationRequest
from models.wristband.tenant import (
    Tenant, 
    TenantUpdateRequest,
    TenantOption,
)
from models.wristband.idp import (
    IdentityProvider,
    UpsertGoogleSamlMetadata,
)

logger = logging.getLogger(__name__)


# MARK: - Dependencies
def get_wristband_service(
    request: Request,
    session: MySession = Depends(get_session)
) -> 'WristbandService':
    return WristbandService(
        request,
        session
    )

# MARK: - Service
class WristbandService:
    def __init__(self, request: Request, session: MySession):
        self.request = request
        self.session = session

    async def login(self) -> Response:
        return await wristband_auth.login(self.request)

    # MARK: - Auth 
    async def callback(self) -> Response:
        callback_result: CallbackResult = await wristband_auth.callback(request=self.request)

        # if redirect required, return redirect response
        if isinstance(callback_result, RedirectRequiredCallbackResult):
            return await wristband_auth.create_callback_response(
                self.request, 
                callback_result.redirect_url
            )
        
        # callback_result is now guaranteed to be CompletedCallbackResult
        roles = [role.name.split(":")[-1] for role in callback_result.callback_data.user_info.roles]
        self.session.from_callback(
            callback_data=callback_result.callback_data, 
            custom_fields={
                "email": callback_result.callback_data.user_info.email,
                "roles": roles,
                "idp_name": callback_result.callback_data.user_info.identity_provider_name,
                "given_name": callback_result.callback_data.user_info.given_name,
                "family_name": callback_result.callback_data.user_info.family_name,
                "picture_url": callback_result.callback_data.user_info.picture_url,
            }
        )
        
        # Return the callback response that redirects to your app.
        return await wristband_auth.create_callback_response(self.request, env.frontend_url)

    async def logout(self) -> Response:
        # Get all necessary session data needed to perform logout
        logout_config = LogoutConfig(
            refresh_token=self.session.refresh_token,
            tenant_custom_domain=self.session.tenant_custom_domain,
            tenant_name=self.session.tenant_name,
            redirect_url=env.frontend_url,
        )

        # Delete the session and CSRF cookies.
        self.session.clear()
        return await wristband_auth.logout(self.request, logout_config)

    async def get_session(self) -> SessionResponse:
        return self.session.get_session_response(metadata={
            "isAuthenticated": self.session.is_authenticated,
            "accessToken": self.session.access_token,
            "expiresAt": self.session.expires_at,
            "userId": self.session.user_id,
            "tenantId": self.session.tenant_id,
            "tenantName": self.session.tenant_name,
            "csrfToken": self.session.csrf_token,
            "refreshToken": self.session.refresh_token,
            "email": self.session.email,
            "idpName": self.session.idp_name,
        })

    # MARK: - User APIs
    async def get_user_info(self, user_id: str | None = None) -> User:
        # Get user data
        user_data = await WristbandClient().get_user_info(
            user_id=user_id or self.session.user_id,
            access_token=self.session.access_token
        )
        
        # Get and attach user roles
        roles_data = await WristbandClient().resolve_assigned_roles_for_users(
            user_ids=[user_data['id']],
            access_token=self.session.access_token
        )
        
        # Extract role SKUs
        user_roles_item = next((item for item in roles_data.get('items', []) if item['userId'] == user_data['id']), None)
        if user_roles_item:
            user_data['roles'] = [role['name'].split(':')[-1] for role in user_roles_item.get('roles', [])]
        else:
            user_data['roles'] = []
        
        return User(**user_data)

    async def update_user_profile(self, update_name_request: UpdateNameRequest) -> User:
        user_data = await WristbandClient().update_user(
            user_id=self.session.user_id,
            data=update_name_request.to_payload(),
            access_token=self.session.access_token
        )
        return User(**user_data)

    async def change_user_password(self, password_data: PasswordChangeRequest) -> None:
        return await WristbandClient().change_password(
            user_id=self.session.user_id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
            access_token=self.session.access_token
        )

    async def get_user_roles(self) -> list[Role]:
        # Get roles data from API
        roles_data = await WristbandClient().resolve_assigned_roles_for_users(
            user_ids=[self.session.user_id],
            access_token=self.session.access_token
        )
        
        # Map dict to Role models
        user_roles_item = next((item for item in roles_data.get('items', []) if item['userId'] == self.session.user_id), None)
        if user_roles_item:
            return [Role(**role_dict) for role_dict in user_roles_item.get('roles', [])]
        return []

    async def update_user_roles(self, user_id: str, new_role_ids: list[str], existing_role_ids: list[str]) -> None:
        client = WristbandClient()
        
        # Get current roles to determine what needs to be removed
        roles_data = await client.resolve_assigned_roles_for_users(
            user_ids=[user_id],
            access_token=self.session.access_token
        )
        
        user_roles_item = next((item for item in roles_data.get('items', []) if item['userId'] == user_id), None)
        current_role_ids = [role['id'] for role in user_roles_item.get('roles', [])] if user_roles_item else []
        
        # Determine roles to keep (existing) + add (new)
        final_role_ids = list(set(existing_role_ids + new_role_ids))
        
        # Determine roles to remove
        roles_to_remove = [role_id for role_id in current_role_ids if role_id not in final_role_ids]
        
        # Unassign roles that should be removed
        if roles_to_remove:
            await client.unassign_roles_from_user(
                user_id=user_id,
                role_ids=roles_to_remove,
                access_token=self.session.access_token
            )
        
        # Add new roles (if any)
        if new_role_ids:
            await client.update_user_role_assignments(
                user_id=user_id,
                role_ids=new_role_ids,
                access_token=self.session.access_token
            )

    async def delete_user(self, user_id: str) -> None:
        await WristbandClient().delete_user(
            user_id=user_id,
            access_token=self.session.access_token
        )

    # MARK: - Users APIs
    async def get_users(self) -> list[User]:
        # Get users data
        users_data = await WristbandClient().query_tenant_users(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        
        # Get roles for all users
        user_ids = [user['id'] for user in users_data]
        roles_data = await WristbandClient().resolve_assigned_roles_for_users(
            user_ids=user_ids,
            access_token=self.session.access_token
        )
        
        # Attach roles to each user
        for user_dict in users_data:
            user_roles_item = next((item for item in roles_data.get('items', []) if item['userId'] == user_dict['id']), None)
            if user_roles_item:
                user_dict['roles'] = [role['name'].split(':')[-1] for role in user_roles_item.get('roles', [])]
            else:
                user_dict['roles'] = []
        
        return [User(**user_dict) for user_dict in users_data]

    async def invite_user(self, email: str, role_ids: list[str]) -> None:
        await WristbandClient().invite_user(
            tenant_id=self.session.tenant_id,
            email=email,
            roles_to_assign=role_ids,
            access_token=self.session.access_token
        )

    async def get_invitations(self) -> list[NewUserInvitationRequest]:
        invitations_data = await WristbandClient().query_new_user_invitation_requests(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        return [NewUserInvitationRequest(**inv) for inv in invitations_data]

    async def get_pending_invitations(self) -> list[NewUserInvitationRequest]:
        invitations_data = await WristbandClient().query_new_user_invitation_requests(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token,
            pending_only=True
        )
        return [NewUserInvitationRequest(**inv) for inv in invitations_data]

    async def cancel_invitation(self, invitation_id: str) -> None:
        await WristbandClient().cancel_new_user_invitation(
            invitation_id=invitation_id,
            access_token=self.session.access_token
        )
        
    # MARK: - Tenant APIs
    async def get_tenant_info(self) -> Tenant:
        tenant_data = await WristbandClient().get_tenant(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        return Tenant(**tenant_data)

    async def update_tenant_info(self, tenant_data: TenantUpdateRequest) -> Tenant:
        updated_data = await WristbandClient().update_tenant(
            tenant_id=self.session.tenant_id,
            data=tenant_data.model_dump(by_alias=True, exclude_unset=True),
            access_token=self.session.access_token
        )
        return Tenant(**updated_data)

    async def get_tenant_options(self) -> list[TenantOption]:
        tenants_data = await WristbandClient().fetch_tenants(
            access_token=self.session.access_token,
            application_id=env.application_id,
            email=self.session.email
        )
        return [TenantOption(**tenant) for tenant in tenants_data]

    # MARK: - Role APIs
    async def get_roles(self) -> list[Role]:
        roles_data = await WristbandClient().query_tenant_roles(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        return [Role(**role) for role in roles_data]

    # MARK: - IDP APIs
    async def get_identity_providers(self) -> list[IdentityProvider]:
        idps_data = await WristbandClient().get_identity_providers(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        return [IdentityProvider(**idp) for idp in idps_data]

    async def upsert_google_saml_idp(self, metadata: UpsertGoogleSamlMetadata) -> dict:
        # Enable tenant-level IDP override toggle first
        await WristbandClient().upsert_idp_override_toggle(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        
        # Upsert the Google IDP
        return await WristbandClient().upsert_google_saml_identity_provider(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token,
            metadata=metadata.model_dump(by_alias=True)
        )

    async def upsert_okta_idp(self, domain_name: str, client_id: str, client_secret: str, enabled: bool = True) -> dict:
        # Enable tenant-level IDP override toggle first
        await WristbandClient().upsert_idp_override_toggle(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        
        # Upsert the Okta IDP
        return await WristbandClient().upsert_okta_identity_provider(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token,
            domain_name=domain_name,
            client_id=client_id,
            client_secret=client_secret,
            enabled=enabled
        )

    async def get_okta_redirect_url(self) -> str | None:
        redirect_configs = await WristbandClient().resolve_idp_redirect_url_overrides(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token
        )
        
        # Find Okta config
        for config in redirect_configs:
            if config.get('identityProviderType') == 'OKTA' and config.get('redirectUrls'):
                return config['redirectUrls'][0].get('redirectUrl')
        return None

    async def test_okta_connection(self) -> bool:
        return await WristbandClient().test_idp_connection(
            tenant_id=self.session.tenant_id,
            access_token=self.session.access_token,
            idp_type='OKTA'
        )