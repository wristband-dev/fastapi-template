import logging

from stores.base import BaseStore
from models.wristband.session import MySession
from models.customer import Customer

logger = logging.getLogger(__name__)


class CustomerStore(BaseStore[Customer]):
    """
    Store for Stripe customers.
    
    Note: Customer records are stored globally (not tenant-scoped) because
    they map tenant_id to Stripe customer_id. The tenant_id is stored as
    a field in the document itself for querying.
    """
    COLLECTION = "customers"

    def __init__(self, session: MySession):
        super().__init__(
            session, 
            self.COLLECTION, 
            Customer,
            use_tenant_scope=False  # Customers are global, with tenant_id as a field
        )
