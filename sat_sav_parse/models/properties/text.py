import enum
import typing

import pydantic

from sat_sav_parse.logger import set_struct_name
from sat_sav_parse.models.properties.base import BaseProperty
from sat_sav_parse.models.properties.enums import PropertyTypeName
from sat_sav_parse.utils import U8EnumDeserializerMixin, U8EnumSerializerMixin

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer

__all__ = (
    "TextArgument",
    "TextArgumentInt",
    "TextArgumentText",
    "TextArgumentType",
    "TextProperty",
    "TextPropertyHistoryType",
    "TextValue",
    "TextValueBase",
    "TextValueNone",
    "TextValueStringTableEntry",
    "TextValueTransform",
    "TextValueWithArguments",
    "deserialize_text_argument",
)


class TextPropertyHistoryType(U8EnumSerializerMixin, U8EnumDeserializerMixin, enum.IntEnum):
    BASE = 0
    NAMED = 1
    ARGUMENT = 3
    TRANSFORM = 10
    STRING_TABLE_ENTRY = 11
    NONE = 255


class TextValueBase(pydantic.BaseModel):
    history_type: typing.Literal[TextPropertyHistoryType.BASE] = TextPropertyHistoryType.BASE
    namespace: str
    key: str
    value: str

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        des.get(TextPropertyHistoryType)
        namespace = des.get_string()
        key = des.get_string()
        value = des.get_string()
        return cls(
            namespace=namespace,
            key=key,
            value=value,
        )


class TextArgumentType(U8EnumSerializerMixin, U8EnumDeserializerMixin, enum.IntEnum):
    INT = 0
    UINT = 1
    GENDER = 5
    FLOAT = 2
    DOUBLE = 3
    TEXT = 4


class TextArgumentInt(pydantic.BaseModel):
    name: str
    value_type: typing.Literal[TextArgumentType.INT] = TextArgumentType.INT
    value: int
    unknown: int

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(TextArgumentType)
        value = des.get_i32()
        unknown = des.get_i32()
        return cls(name=name, value=value, unknown=unknown)


class TextArgumentText(pydantic.BaseModel):
    name: str
    value_type: typing.Literal[TextArgumentType.TEXT] = TextArgumentType.TEXT
    value: "TextValue"

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(TextArgumentType)
        value = des.get_fn(TextProperty.deserialize_property_value)
        return cls(name=name, value=value)


type TextArgument = typing.Annotated[
    TextArgumentInt | TextArgumentText,
    pydantic.Field(discriminator="value_type"),
]


@set_struct_name("TextArgument")
def deserialize_text_argument(des: "SFSaveDeserializer") -> TextArgument:
    offset, _ = des.parse_string(des.offset, des.content)
    value_type = des.parse(offset, des.content, TextArgumentType)
    match value_type:
        case TextArgumentType.INT:
            return des.get(TextArgumentInt)
        case TextArgumentType.TEXT:
            return des.get(TextArgumentText)
        case _:
            raise NotImplementedError(f"Deserializer for {value_type!r} not implemented")


class TextValueWithArguments(pydantic.BaseModel):
    history_type: typing.Literal[TextPropertyHistoryType.NAMED, TextPropertyHistoryType.ARGUMENT] = (
        TextPropertyHistoryType.NAMED
    )

    source_format: "TextValue"
    flags: int
    arguments: list[TextArgument]

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        flags = des.get_u32()
        history_type = typing.cast(
            "typing.Literal[TextPropertyHistoryType.NAMED, TextPropertyHistoryType.ARGUMENT]",
            des.get(TextPropertyHistoryType),
        )
        source_format = des.get_fn(TextProperty.deserialize_property_value)
        argument_count = des.get_u32()
        arguments = [des.get_fn(deserialize_text_argument) for _ in range(argument_count)]
        return cls(
            history_type=history_type,
            source_format=source_format,
            flags=flags,
            arguments=arguments,
        )


class TextValueTransform(pydantic.BaseModel):
    history_type: typing.Literal[TextPropertyHistoryType.TRANSFORM] = TextPropertyHistoryType.TRANSFORM
    source_text: "TextValue"
    transform_type: int
    flags: int

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        flags = des.get_u32()
        des.get(TextPropertyHistoryType)
        source_text = des.get_fn(TextProperty.deserialize_property_value)
        transform_type = des.get_u8()
        return cls(
            source_text=source_text,
            transform_type=transform_type,
            flags=flags,
        )


class TextValueStringTableEntry(pydantic.BaseModel):
    history_type: typing.Literal[TextPropertyHistoryType.STRING_TABLE_ENTRY] = (
        TextPropertyHistoryType.STRING_TABLE_ENTRY
    )
    table_id: str
    table_key: str
    flags: int

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        flags = des.get_u32()
        des.get(TextPropertyHistoryType)
        table_id = des.get_string()
        table_key = des.get_string()
        return cls(
            table_id=table_id,
            table_key=table_key,
            flags=flags,
        )


class TextValueNone(pydantic.BaseModel):
    history_type: typing.Literal[TextPropertyHistoryType.NONE] = TextPropertyHistoryType.NONE
    has_culture_invariant_string: bool
    value: str
    flags: int

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        flags = des.get_u32()
        des.get(TextPropertyHistoryType)
        has_culture_invariant_string = des.get_u32_bool()
        value = des.get_string()
        return cls(
            has_culture_invariant_string=has_culture_invariant_string,
            value=value,
            flags=flags,
        )


type TextValue = typing.Annotated[
    TextValueBase | TextValueWithArguments | TextValueTransform | TextValueStringTableEntry | TextValueNone,
    pydantic.Field(discriminator="history_type"),
]


class TextProperty(BaseProperty[TextValue]):
    type_name: typing.Literal[PropertyTypeName.TEXT] = PropertyTypeName.TEXT
    index: int

    @classmethod
    @set_struct_name("TextValue")
    def deserialize_property_value(cls, des: "SFSaveDeserializer") -> TextValue:
        offset, _ = des.parse_u32(des.offset, des.content)
        history_type = des.parse(offset, des.content, TextPropertyHistoryType)
        match history_type:
            case TextPropertyHistoryType.BASE:
                return des.get(TextValueBase)
            case TextPropertyHistoryType.NAMED:
                return des.get(TextValueWithArguments)
            case TextPropertyHistoryType.ARGUMENT:
                return des.get(TextValueWithArguments)
            case TextPropertyHistoryType.TRANSFORM:
                return des.get(TextValueTransform)
            case TextPropertyHistoryType.STRING_TABLE_ENTRY:
                return des.get(TextValueStringTableEntry)
            case TextPropertyHistoryType.NONE:
                return des.get(TextValueNone)
            case _:
                typing.assert_never(history_type)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        des.get_u8()

        return cls(
            name=name,
            payload_size=payload_size,
            index=index,
            payload=des.get_fn(cls.deserialize_property_value),
        )
