import base64
import typing
from contextlib import contextmanager

from sat_sav_parse.exceptions import ParseError
from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = (
    "StrEnumDeserializerMixin",
    "StrEnumSerializerMixin",
    "U8EnumDeserializerMixin",
    "U8EnumSerializerMixin",
    "U32EnumDeserializerMixin",
    "U32EnumSerializerMixin",
    "expect_size",
)


@contextmanager
def expect_size(p: SFSaveDeserializer, size: int, what: str):
    start = p.offset
    yield
    diff = p.offset - start
    if diff != size:
        raise ParseError("invalid_size", f"{what}: invalid size {diff}, expected {size}")


class StrEnumSerializerMixin:
    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self)  # type: ignore


class StrEnumDeserializerMixin:
    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(des.get_string())  # type: ignore


class U8EnumSerializerMixin:
    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_u8(self)  # type: ignore


class U8EnumDeserializerMixin:
    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(des.get_u8())  # type: ignore


class U32EnumSerializerMixin:
    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_u32(self)  # type: ignore


class U32EnumDeserializerMixin:
    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(des.get_u32())  # type: ignore


def b64_bytes[T](v: T) -> T:
    if isinstance(v, bytes):
        return base64.b64encode(v).decode("ascii")  # type: ignore
    return v
