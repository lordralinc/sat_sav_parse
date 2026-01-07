import functools
import logging
import typing

import pydantic

from sat_sav_parse.models.object_reference import ObjectReference
from sat_sav_parse.models.properties.base import BaseProperty
from sat_sav_parse.models.properties.enums import (
    ArrayElementTypeName,
    PropertyTypeName,
    StructTypeName,
)
from sat_sav_parse.models.properties.typed_data import (
    StructValue,
    deserialize_struct_value,
)
from sat_sav_parse.utils import b64_bytes, expect_size

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer


__all__ = (
    "ArrayElementByte",
    "ArrayElementEnum",
    "ArrayElementFloat",
    "ArrayElementInt",
    "ArrayElementInt64",
    "ArrayElementInterface",
    "ArrayElementObject",
    "ArrayElementSoftObject",
    "ArrayElementStr",
    "ArrayElementStruct",
    "ArrayElementStructValueType",
    "ArrayElementType",
    "ArrayProperty",
    "BaseArrayElement",
)


logger = logging.getLogger()


class BaseArrayElement[T](pydantic.BaseModel):
    length: int
    elements: T


class ArrayElementByte(BaseArrayElement[list[int]]):
    type: typing.Literal[ArrayElementTypeName.BYTE] = ArrayElementTypeName.BYTE

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get_u8() for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementEnum(BaseArrayElement[list[str]]):
    type: typing.Literal[ArrayElementTypeName.ENUM] = ArrayElementTypeName.ENUM

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get_string() for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementStr(BaseArrayElement[list[str]]):
    type: typing.Literal[ArrayElementTypeName.STR] = ArrayElementTypeName.STR

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get_string() for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementInterface(BaseArrayElement[list[ObjectReference]]):
    type: typing.Literal[ArrayElementTypeName.INTERFACE] = ArrayElementTypeName.INTERFACE

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get(ObjectReference) for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementObject(BaseArrayElement[list[ObjectReference]]):
    type: typing.Literal[ArrayElementTypeName.OBJECT] = ArrayElementTypeName.OBJECT

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get(ObjectReference) for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementInt(BaseArrayElement[list[int]]):
    type: typing.Literal[ArrayElementTypeName.INT] = ArrayElementTypeName.INT

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get_i32() for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementInt64(BaseArrayElement[list[int]]):
    type: typing.Literal[ArrayElementTypeName.INT64] = ArrayElementTypeName.INT64

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get_i64() for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementFloat(BaseArrayElement[list[float]]):
    type: typing.Literal[ArrayElementTypeName.FLOAT] = ArrayElementTypeName.FLOAT

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [des.get_float() for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


class ArrayElementSoftObject(BaseArrayElement[list[tuple[ObjectReference, int]]]):
    type: typing.Literal[ArrayElementTypeName.SOFT_OBJECT] = ArrayElementTypeName.SOFT_OBJECT

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()
        elements = [(des.get(ObjectReference), des.get_u32()) for _ in range(length)]
        return cls(
            length=length,
            elements=elements,
        )


type ArrayElementStructValueType = list[StructValue] | pydantic.Base64Bytes


class ArrayElementStruct(BaseArrayElement[ArrayElementStructValueType]):
    type: typing.Literal[ArrayElementTypeName.STRUCT] = ArrayElementTypeName.STRUCT
    name: str
    type_name: str
    payload_size: int
    element_type: StructTypeName
    uuid: pydantic.Base64Bytes

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        length = des.get_u32()

        name = des.get_string()

        type_name = des.get_string()
        payload_size = des.get_u32()
        des.get_u32()

        element_type = des.get(StructTypeName)

        uuid = des.get_item(17)

        with expect_size(des, payload_size, "ArrayElementStruct"):
            elements = []

            for _ in range(length):
                element = des.get_fn(
                    functools.partial(
                        deserialize_struct_value,
                        struct_type=element_type,
                        payload_size=payload_size,
                    ),
                )
                if isinstance(element, bytes):
                    elements = element
                    break
                elements.append(element)
        return cls(
            length=length,
            elements=b64_bytes(elements),
            name=name,
            type_name=type_name,
            payload_size=payload_size,
            element_type=element_type,
            uuid=b64_bytes(uuid),
        )


type ArrayElementType = typing.Annotated[
    ArrayElementByte
    | ArrayElementEnum
    | ArrayElementStr
    | ArrayElementInterface
    | ArrayElementObject
    | ArrayElementInt
    | ArrayElementInt64
    | ArrayElementFloat
    | ArrayElementSoftObject
    | ArrayElementStruct,
    pydantic.Field(discriminator="type"),
]


class ArrayProperty(BaseProperty[ArrayElementType]):
    type_name: typing.Literal[PropertyTypeName.ARRAY] = PropertyTypeName.ARRAY
    index: int

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        element_type = des.get(ArrayElementTypeName)
        des.confirm_basic_type(des.parse_u8, 0)
        with expect_size(des, payload_size, "ArrayProperty"):
            match element_type:
                case ArrayElementTypeName.BYTE:
                    value = des.get(ArrayElementByte)
                case ArrayElementTypeName.ENUM:
                    value = des.get(ArrayElementEnum)
                case ArrayElementTypeName.STR:
                    value = des.get(ArrayElementStr)
                case ArrayElementTypeName.INTERFACE:
                    value = des.get(ArrayElementInterface)
                case ArrayElementTypeName.OBJECT:
                    value = des.get(ArrayElementObject)
                case ArrayElementTypeName.INT:
                    value = des.get(ArrayElementInt)
                case ArrayElementTypeName.INT64:
                    value = des.get(ArrayElementInt64)
                case ArrayElementTypeName.FLOAT:
                    value = des.get(ArrayElementFloat)
                case ArrayElementTypeName.SOFT_OBJECT:
                    value = des.get(ArrayElementSoftObject)
                case ArrayElementTypeName.STRUCT:
                    value = des.get(ArrayElementStruct)
                case _:
                    typing.assert_never(element_type)
        return cls(name=name, payload_size=payload_size, index=index, payload=value)
