from typing import TypeVar, Generic, List, Optional
from models.wristband.session import MySession
from models import BaseDatabaseProtocol
from database.doc_store import (
    get_document,
    add_document,
    update_document,
    set_document,
    query_documents,
    delete_document,
    doc_exists,
)


T = TypeVar("T", bound=BaseDatabaseProtocol)


class BaseStore(Generic[T]):
    """
    Generic base store for Firestore collections with tenant scoping support.
    
    All database operations are automatically scoped to the current tenant
    when use_tenant_scope is True (default).
    """
    
    def __init__(
        self,
        session: MySession,
        collection_name: str,
        model_class: type[T],
        use_tenant_scope: bool = True,
    ):
        self.collection_name = collection_name
        self.session = session
        self.model_class = model_class
        self.use_tenant_scope = use_tenant_scope
        self.tenant_id: Optional[str] = session.tenant_id if use_tenant_scope else None

    def add(self, data: T, doc_id: str | None = None) -> str:
        """Add a new document to the store"""
        doc_id = add_document(
            collection_path=self.collection_name,
            data=data.to_db_create(),
            tenant_id=self.tenant_id,
        )
        return doc_id

    def update(self, doc_id: str, data: T) -> None:
        """Update an existing document"""
        update_document(
            collection_path=self.collection_name,
            doc_id=doc_id,
            data=data.to_db_update(),
            tenant_id=self.tenant_id,
        )

    def set(self, doc_id: str, data: T) -> str:
        """Set (upsert) a document"""
        set_document(
            collection_path=self.collection_name,
            doc_id=doc_id,
            data=data.to_db_create(),
            tenant_id=self.tenant_id,
        )
        return doc_id

    def get(self, doc_id: str) -> T:
        """Get a single document by ID"""
        data = get_document(
            collection_path=self.collection_name,
            doc_id=doc_id,
            tenant_id=self.tenant_id,
        )
        if data is None:
            raise ValueError(f"Document not found with ID {doc_id}")
        return self.model_class.from_db(data)

    def get_or_none(self, doc_id: str) -> Optional[T]:
        """Get a single document by ID, or None if not found"""
        data = get_document(
            collection_path=self.collection_name,
            doc_id=doc_id,
            tenant_id=self.tenant_id,
        )
        if data is None:
            return None
        return self.model_class.from_db(data)

    def exists(self, doc_id: str) -> bool:
        """Check if a document exists"""
        return doc_exists(
            collection_path=self.collection_name,
            doc_id=doc_id,
            tenant_id=self.tenant_id,
        )

    def delete(self, doc_id: str) -> bool:
        """Delete a document"""
        return delete_document(
            collection_path=self.collection_name,
            doc_id=doc_id,
            tenant_id=self.tenant_id,
        )

    def get_all(self) -> List[T]:
        """Get all documents in the collection"""
        docs = query_documents(
            collection_path=self.collection_name,
            tenant_id=self.tenant_id,
        )
        return [self.model_class.from_db(doc) for doc in docs]

    def get_by_field(self, field: str, value: str) -> List[T]:
        """Get all documents matching a field value"""
        docs = query_documents(
            collection_path=self.collection_name,
            tenant_id=self.tenant_id,
            where_field=field,
            where_operator="==",
            where_value=value,
        )
        return [self.model_class.from_db(doc) for doc in docs]
