import typing

import pydantic

from sat_sav_parse.logger import set_struct_name

from .array import (
    ArrayElementByte,
    ArrayElementEnum,
    ArrayElementFloat,
    ArrayElementInt,
    ArrayElementInt64,
    ArrayElementInterface,
    ArrayElementObject,
    ArrayElementSoftObject,
    ArrayElementStr,
    ArrayElementStruct,
    ArrayElementStructValueType,
    ArrayElementType,
    ArrayProperty,
    BaseArrayElement,
)
from .base import BaseProperty
from .enums import (
    ArrayElementTypeName,
    PropertyTypeName,
    StructTypeName,
)
from .map import (
    KeyTypeName,
    MapKeyType,
    MapKeyValue,
    MapProperty,
    ValueTypeName,
)
from .set import SetProperty, SetType
from .simple_preperties import (
    BoolProperty,
    ByteProperty,
    DoubleProperty,
    EnumProperty,
    FloatProperty,
    Int8Property,
    Int64Property,
    IntProperty,
    NameProperty,
    ObjectProperty,
    SoftObjectProperty,
    StrProperty,
    UInt32Property,
)
from .struct import StructProperty
from .text import (
    TextArgument,
    TextArgumentInt,
    TextArgumentText,
    TextArgumentType,
    TextProperty,
    TextPropertyHistoryType,
    TextValue,
    TextValueBase,
    TextValueNone,
    TextValueStringTableEntry,
    TextValueTransform,
    TextValueWithArguments,
    deserialize_text_argument,
)
from .typed_data import (
    Box,
    ClientIdentityInfo,
    ClientIdentityInfoIdentity,
    ClientIdentityInfoIdentityVariant,
    DateTime,
    FluidBox,
    InventoryItem,
    LinearColor,
    Quat,
    RailroadTrackPosition,
    SpawnData,
    Vector,
)

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
    "ArrayElementTypeName",
    "ArrayProperty",
    "BaseArrayElement",
    "BaseProperty",
    "BoolProperty",
    "Box",
    "ByteProperty",
    "ClientIdentityInfo",
    "ClientIdentityInfoIdentity",
    "ClientIdentityInfoIdentityVariant",
    "DateTime",
    "DoubleProperty",
    "EnumProperty",
    "FloatProperty",
    "FluidBox",
    "Int8Property",
    "Int64Property",
    "IntProperty",
    "InventoryItem",
    "KeyTypeName",
    "LinearColor",
    "MapKeyType",
    "MapKeyValue",
    "MapProperty",
    "NameProperty",
    "ObjectProperty",
    "PropertyType",
    "PropertyTypeName",
    "Quat",
    "RailroadTrackPosition",
    "SetProperty",
    "SetType",
    "SoftObjectProperty",
    "SpawnData",
    "StrProperty",
    "StructProperty",
    "StructTypeName",
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
    "UInt32Property",
    "ValueTypeName",
    "Vector",
    "deserialize_properties",
    "deserialize_text_argument",
)

type PropertyType = typing.Annotated[
    ArrayProperty
    | BoolProperty
    | ByteProperty
    | DoubleProperty
    | EnumProperty
    | FloatProperty
    | Int8Property
    | Int64Property
    | IntProperty
    | NameProperty
    | ObjectProperty
    | SoftObjectProperty
    | StrProperty
    | UInt32Property
    | TextProperty
    | SetProperty
    | StructProperty
    | MapProperty,
    pydantic.Field(discriminator="type_name"),
]


@set_struct_name("PropertyList")
def deserialize_properties(des: "SFSaveDeserializer") -> list[PropertyType]:
    properties = []

    while True:
        next_offset, name = des.parse_string(des.offset, des.content)
        if name == "None":
            des.offset = next_offset
            break
        property_type = des.parse(next_offset, des.content, PropertyTypeName)

        match property_type:
            case PropertyTypeName.ARRAY:
                properties.append(des.get(ArrayProperty))
            case PropertyTypeName.BOOL:
                properties.append(des.get(BoolProperty))
            case PropertyTypeName.BYTE:
                properties.append(des.get(ByteProperty))
            case PropertyTypeName.ENUM:
                properties.append(des.get(EnumProperty))
            case PropertyTypeName.FLOAT:
                properties.append(des.get(FloatProperty))
            case PropertyTypeName.DOUBLE:
                properties.append(des.get(DoubleProperty))
            case PropertyTypeName.INT:
                properties.append(des.get(IntProperty))
            case PropertyTypeName.INT8:
                properties.append(des.get(Int8Property))
            case PropertyTypeName.U_INT32:
                properties.append(des.get(UInt32Property))
            case PropertyTypeName.INT64:
                properties.append(des.get(Int64Property))
            case PropertyTypeName.NAME:
                properties.append(des.get(NameProperty))
            case PropertyTypeName.OBJECT:
                properties.append(des.get(ObjectProperty))
            case PropertyTypeName.SOFT_OBJECT:
                properties.append(des.get(SoftObjectProperty))
            case PropertyTypeName.STR:
                properties.append(des.get(StrProperty))
            case PropertyTypeName.TEXT:
                properties.append(des.get(TextProperty))
            case PropertyTypeName.SET:
                properties.append(des.get(SetProperty))
            case PropertyTypeName.STRUCT:
                properties.append(des.get(StructProperty))
            case PropertyTypeName.MAP:
                properties.append(des.get(MapProperty))
            case _:
                typing.assert_never(property_type)
    return properties
