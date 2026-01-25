from pydantic import BaseModel as BM, ConfigDict, Field
from datetime import datetime, timezone
from typing import Protocol, Self


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


COMPUTED_FIELDS_TO_INCLUDE = {"hash_value"}


class BaseDatabaseProtocol(Protocol):
    """Protocol for all models that are written to the database"""
    created_at: datetime
    updated_at: datetime

    def to_db_create(self) -> dict: ...
    def to_db_update(self) -> dict: ...

    @classmethod
    def from_db(cls, data: dict) -> Self: ...


class BaseModel(BM):
    """BaseModel to be used for all models in this project"""

    # converts snake_case to camelCase
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class BaseDatabaseModel(BaseModel):
    """BaseModel for all models that are written to the database"""

    # expose timestamp fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def computed_fields(self) -> set[str]:
        return set(self.__class__.model_computed_fields.keys())

    def to_db_update(self) -> dict:
        data = self.model_dump(
            mode="json",
            exclude=(self.computed_fields - COMPUTED_FIELDS_TO_INCLUDE) | {"created_at"},
            exclude_none=True,
        )
        # Always set updated_at to current time when updating
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        return data

    def to_db_create(self) -> dict:
        data = self.model_dump(
            mode="json",
            exclude=(self.computed_fields - COMPUTED_FIELDS_TO_INCLUDE),
            exclude_none=True,
        )
        return data

    @classmethod
    def from_db(cls, data: dict) -> Self:
        """Create model instance from database data"""
        return cls(**data)
