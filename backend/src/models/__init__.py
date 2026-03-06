from pydantic import BaseModel as BM, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


COMPUTED_FIELDS_TO_INCLUDE = {"hash_value"}


class BaseModel(BM):
    """Pydantic BaseModel with camelCase aliases for API request/response models."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
