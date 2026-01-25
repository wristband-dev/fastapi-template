import os
from dotenv import load_dotenv
import logging
from enum import Enum

from utils.singleton import singleton

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


class EnvironmentType(Enum):
    DEV = "DEV"
    PROD = "PROD"
    STAGING = "STAGING"

    def get_database_id(self) -> str:
        return self.value.lower() + "-db"

def get_environment() -> EnvironmentType:
    # if ENVIRONMENT is not set or is set to DEV
    env_value = os.environ.get("ENVIRONMENT", "DEV")
    if env_value == "DEV":
        # load from .env.local
        if os.getcwd().endswith('backend'):
            load_dotenv('.env.local')
            logger.debug("Loaded environment variables from .env.local")
        else:
            load_dotenv('backend/.env.local')
            logger.debug("Loaded environment variables from backend/.env.local")
    
    # Now get the environment type after loading .env.local
    type = EnvironmentType(os.environ.get("ENVIRONMENT", "DEV"))
    return type

@singleton
class Environment:
    def __init__(self):
        logger.info("Getting Environment")
        self.type: EnvironmentType = get_environment()
        self.database_id: str = self.type.get_database_id()
        self.frontend_url: str  = self._get_frontend_url()
        self.backend_url: str  = self._get_backend_url()
        self.client_id: str  = self._get_client_id()
        self.client_secret: str  = self._get_client_secret()
        self.application_vanity_domain: str  = self._get_application_vanity_domain()
        self.application_id: str  = self._get_application_id()

        logger.debug(f"Environment Type: {self.type}")
        logger.debug(f"Database ID: {self.database_id}")
        logger.debug(f"Frontend URL: {self.frontend_url}")
        logger.debug(f"Backend URL: {self.backend_url}")
        logger.debug(f"Client ID: {self.client_id}")
        logger.debug(f"Client Secret: {self.client_secret}")
        logger.debug(f"Application Vanity Domain: {self.application_vanity_domain}")
        logger.debug(f"Application ID: {self.application_id}")

    @property
    def is_dev(self) -> bool:
        return self.type == EnvironmentType.DEV

    @property
    def is_prod(self) -> bool:
        return self.type == EnvironmentType.PROD
    
    @property
    def is_staging(self) -> bool:
        return self.type == EnvironmentType.STAGING

    @property
    def is_deployed(self) -> bool:
        return self.is_staging or self.is_prod

    def _get_domain_name(self) -> str | None:
        return os.environ.get("DOMAIN_NAME")

    def _get_domain_name_url(self,) -> str:
        domain_name = self._get_domain_name()
        return f"https://{domain_name}"

    def _get_frontend_url(self) -> str:
        if self.is_deployed:
            return self._get_domain_name_url()
        else:
            return f"http://localhost:3001"

    def _get_backend_url(self) -> str:
        if self.is_deployed:
            return self._get_domain_name_url()
        else:
            return f"http://localhost:6001"

    def _get_client_id(self) -> str:
        client_id = os.environ.get("CLIENT_ID")
        if client_id is None:
            raise ValueError("CLIENT_ID is not set")
        return client_id

    def _get_client_secret(self) -> str:
        client_secret = os.environ.get("CLIENT_SECRET")
        if client_secret is None:
            raise ValueError("CLIENT_SECRET is not set")
        return client_secret
    
    def _get_application_vanity_domain(self) -> str:
        application_vanity_domain = os.environ.get("APPLICATION_VANITY_DOMAIN")
        if application_vanity_domain is None:
            raise ValueError("APPLICATION_VANITY_DOMAIN is not set")
        return application_vanity_domain

    def _get_application_id(self) -> str:
        application_id = os.environ.get("APPLICATION_ID")
        if application_id is None:
            raise ValueError("APPLICATION_ID is not set")
        return application_id

    def get_stripe_secret_key(self) -> str:
        stripe_secret_key = os.environ.get("STRIPE_SECRET_KEY")
        if stripe_secret_key is None:
            raise ValueError("STRIPE_SECRET_KEY is not set")
        return stripe_secret_key

environment = Environment()