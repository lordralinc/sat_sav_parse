import enum
import typing

from sat_sav_parse.models.properties.array import ObjectReference
from sat_sav_parse.models.properties.base import BaseProperty
from sat_sav_parse.models.properties.enums import PropertyTypeName, StrEnumSerializerMixin
from sat_sav_parse.models.properties.text import TextProperty, TextValue
from sat_sav_parse.utils import StrEnumDeserializerMixin, expect_size

if typing.TYPE_CHECKING:
    from sat_sav_parse.models.properties import PropertyType
    from sat_sav_parse.structs import SFSaveDeserializer

__all__ = (
    "KeyTypeName",
    "MapKeyType",
    "MapKeyValue",
    "MapProperty",
    "ValueTypeName",
)


class KeyTypeName(StrEnumSerializerMixin, StrEnumDeserializerMixin, enum.StrEnum):
    OBJECT = "ObjectProperty"
    INT = "IntProperty"
    INT64 = "Int64Property"
    NAME = "NameProperty"
    STR = "StrProperty"
    ENUM = "EnumProperty"
    STRUCT = "StructProperty"


class ValueTypeName(StrEnumSerializerMixin, StrEnumDeserializerMixin, enum.StrEnum):
    BYTE = "ByteProperty"
    BOOL = "BoolProperty"
    INT = "IntProperty"
    INT64 = "Int64Property"
    FLOAT = "FloatProperty"
    DOUBLE = "DoubleProperty"
    STR = "StrProperty"
    OBJECT = "ObjectProperty"
    TEXT = "TextProperty"
    STRUCT = "StructProperty"


type MapKeyType = tuple[str, str] | int | str | tuple[int, int, int]
type MapKeyValue = "int | str | ObjectReference | float | list[PropertyType] | TextValue"


class MapProperty(BaseProperty[dict[MapKeyType, MapKeyValue]]):
    type_name: typing.Literal[PropertyTypeName.MAP] = PropertyTypeName.MAP
    index: int
    key_type: KeyTypeName
    value_type: ValueTypeName
    mode: int
    elements_count: int

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        from sat_sav_parse.models.properties import deserialize_properties  # noqa: PLC0415

        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        key_type = des.get(KeyTypeName)
        value_type = des.get(ValueTypeName)
        des.get_u8()
        with expect_size(des, payload_size, "MapProperty"):
            mode = des.get_u32()
            elements_count = des.get_u32()

            elemets = {}

            for _ in range(elements_count):
                match key_type:
                    case KeyTypeName.INT:
                        key = des.get_i32()
                    case KeyTypeName.INT64:
                        key = des.get_i64()
                    case KeyTypeName.NAME:
                        key = des.get_string()
                    case KeyTypeName.STR:
                        key = des.get_string()
                    case KeyTypeName.ENUM:
                        key = des.get_string()
                    case KeyTypeName.OBJECT:
                        ref = des.get(ObjectReference)
                        key = (ref.level_name, ref.path_name)
                    case KeyTypeName.STRUCT:
                        key = (des.get_i32(), des.get_i32(), des.get_i32())
                    case _:
                        typing.assert_never(key_type)
                match value_type:
                    case ValueTypeName.BYTE:
                        value = des.get_string() if key_type == KeyTypeName.STR else des.get_u8()
                    case ValueTypeName.BOOL:
                        value = des.get_u8_bool()
                    case ValueTypeName.INT:
                        value = des.get_i32()
                    case ValueTypeName.INT64:
                        value = des.get_i64()
                    case ValueTypeName.FLOAT:
                        value = des.get_float()
                    case ValueTypeName.DOUBLE:
                        value = des.get_double()
                    case ValueTypeName.STR:
                        value = des.get_string()
                    case ValueTypeName.OBJECT:
                        value = des.get(ObjectReference)
                    case ValueTypeName.TEXT:
                        value = des.get_fn(TextProperty.deserialize_property_value)
                    case ValueTypeName.STRUCT:
                        value = des.get_fn(deserialize_properties)
                    case _:
                        typing.assert_never(value_type)
                elemets[key] = value
        return cls(
            name=name,
            payload_size=payload_size,
            index=index,
            key_type=key_type,
            value_type=value_type,
            mode=mode,
            elements_count=elements_count,
            payload=elemets,
        )
