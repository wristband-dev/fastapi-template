"""Schema base models — DatabaseModel, DBMixin, ResponseDatabaseModel.

Adapted from wedge-golf-app. Provides model-level CRUD so you can write:
    customer = Customer.get(42)
    customer = Customer.find(tenant_id="abc")
    Customer.create(CustomerCreate(...))
"""

from typing import Type, TypeVar, Self, ClassVar, Sequence
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from database import get_engine


T = TypeVar("T", bound="DatabaseModel")
R = TypeVar("R", bound="ResponseDatabaseModel")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DatabaseModel(SQLModel):
    """Base model with timestamps — inherited by all models."""

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class DBMixin:
    """Database operations mixin — add to DB table models.

    Provides get_by_id, find_by, filter_by, save, delete, delete_by, query_all.
    """

    @classmethod
    def _get_session(cls) -> Session:
        engine = get_engine()
        if not engine:
            raise RuntimeError("No database connection")
        return Session(engine)

    @classmethod
    def query_all(cls: Type[T]) -> list[T]:  # pyright: ignore[reportGeneralTypeIssues]
        with cls._get_session() as session:  # type: ignore[attr-defined]
            return list(session.exec(select(cls)).all())

    @classmethod
    def get_by_id(
        cls: Type[T], id: int  # pyright: ignore[reportGeneralTypeIssues]
    ) -> T | None:
        with cls._get_session() as session:  # type: ignore[attr-defined]
            return session.get(cls, id)

    @classmethod
    def find_by(
        cls: Type[T], **kwargs  # pyright: ignore[reportGeneralTypeIssues]
    ) -> T | None:
        with cls._get_session() as session:  # type: ignore[attr-defined]
            statement = select(cls).filter_by(**kwargs)
            return session.exec(statement).first()

    @classmethod
    def filter_by(
        cls: Type[T], **kwargs  # pyright: ignore[reportGeneralTypeIssues]
    ) -> list[T]:
        with cls._get_session() as session:  # type: ignore[attr-defined]
            statement = select(cls).filter_by(**kwargs)
            return list(session.exec(statement).all())

    def save(self: Self) -> Self:
        self.updated_at = datetime.now(timezone.utc)  # type: ignore[attr-defined]
        with self._get_session() as session:  # type: ignore[attr-defined]
            session.add(self)
            session.commit()
            session.refresh(self)
        return self

    @classmethod
    def delete_by(cls, **kwargs) -> int:
        """Delete records matching kwargs. Returns count deleted."""
        with cls._get_session() as session:
            statement = select(cls).filter_by(**kwargs)
            records = session.exec(statement).all()
            count = len(records)
            for record in records:
                session.delete(record)
            session.commit()
            return count

    def delete(self) -> None:
        with self._get_session() as session:  # type: ignore[attr-defined]
            session.delete(self)
            session.commit()


class ResponseDatabaseModel(DatabaseModel):
    """Base for response models with CRUD operations.

    Subclasses must set __db_model__ to the corresponding DB table class.
    Usage:
        customer = Customer.get(42)
        customer = Customer.find(tenant_id="abc")
        customers = Customer.query(tenant_id="abc")
        Customer.create(CustomerCreate(...))
        Customer.update(42, email="new@email.com")
        Customer.delete(tenant_id="abc")
    """

    __db_model__: ClassVar[Type["DBMixin"]]

    @classmethod
    def create(cls: Type[R], data: DatabaseModel) -> R:
        db_obj = cls.__db_model__(**data.model_dump())
        db_obj.save()  # type: ignore[attr-defined]
        return cls.model_validate(db_obj)

    @classmethod
    def get(cls: Type[R], id: int) -> R | None:
        db_obj = cls.__db_model__.get_by_id(id)  # type: ignore[attr-defined]
        return cls.model_validate(db_obj) if db_obj else None

    @classmethod
    def find(cls: Type[R], **kwargs) -> R | None:
        db_obj = cls.__db_model__.find_by(**kwargs)  # type: ignore[attr-defined]
        return cls.model_validate(db_obj) if db_obj else None

    @classmethod
    def query(cls: Type[R], **kwargs) -> list[R]:
        """Query records. No args = all, with args = filter."""
        if kwargs:
            db_objs = cls.__db_model__.filter_by(**kwargs)  # type: ignore[attr-defined]
        else:
            db_objs = cls.__db_model__.query_all()  # type: ignore[attr-defined]
        return [cls.model_validate(obj) for obj in db_objs]

    @classmethod
    def delete(cls, **kwargs) -> int:
        """Delete records matching criteria. Returns count deleted."""
        return cls.__db_model__.delete_by(**kwargs)

    @classmethod
    def update(cls: Type[R], id: int, **kwargs) -> R:
        """Update a record by ID with the given fields."""
        db_obj = cls.__db_model__.get_by_id(id)  # type: ignore[attr-defined]
        if not db_obj:
            raise ValueError(f"Record with id {id} not found")
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        db_obj.save()  # type: ignore[attr-defined]
        return cls.model_validate(db_obj)

    @classmethod
    def upsert(
        cls: Type[R], data: DatabaseModel, index_elements: str | Sequence[str]
    ) -> R:
        """Insert or update a record based on conflict fields."""
        if isinstance(index_elements, str):
            index_elements = [index_elements]

        values = data.model_dump()
        values["updated_at"] = datetime.now(timezone.utc)

        with cls.__db_model__._get_session() as session:  # type: ignore[attr-defined]
            stmt = insert(cls.__db_model__).values(**values)
            stmt = stmt.on_conflict_do_update(
                index_elements=index_elements,
                set_={
                    k: v
                    for k, v in values.items()
                    if k not in index_elements and k != "created_at"
                },
            )
            session.execute(stmt)
            session.commit()

            filter_kwargs = {k: values[k] for k in index_elements}
            db_obj = cls.__db_model__.find_by(**filter_kwargs)  # type: ignore[attr-defined]
            return cls.model_validate(db_obj)
