import pydantic

__all__ = ("BaseProperty",)


class BaseProperty[T](pydantic.BaseModel):
    name: str
    payload_size: int
    payload: T
