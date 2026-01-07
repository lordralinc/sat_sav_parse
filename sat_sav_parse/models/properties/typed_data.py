import enum
import logging
import typing

import pydantic

from sat_sav_parse.logger import set_struct_name
from sat_sav_parse.models.object_reference import ObjectReference
from sat_sav_parse.models.properties.enums import StructTypeName
from sat_sav_parse.utils import ParseError, U8EnumDeserializerMixin, U8EnumSerializerMixin, b64_bytes, expect_size

if typing.TYPE_CHECKING:
    from sat_sav_parse.models.properties import PropertyType
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer


__all__ = (
    "Box",
    "ClientIdentityInfo",
    "ClientIdentityInfoIdentity",
    "ClientIdentityInfoIdentityVariant",
    "DateTime",
    "FluidBox",
    "InventoryItem",
    "LinearColor",
    "Quat",
    "RailroadTrackPosition",
    "SpawnData",
    "Vector",
)

logger = logging.getLogger(__name__)


class Box(pydantic.BaseModel):
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float
    is_valid: bool

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_double(self.min_x)
        ser.add_double(self.min_y)
        ser.add_double(self.min_z)
        ser.add_double(self.max_x)
        ser.add_double(self.max_y)
        ser.add_double(self.max_z)
        ser.add_u8_bool(self.is_valid)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            min_x=des.get_double(),
            min_y=des.get_double(),
            min_z=des.get_double(),
            max_x=des.get_double(),
            max_y=des.get_double(),
            max_z=des.get_double(),
            is_valid=des.get_u8_bool(),
        )


class FluidBox(pydantic.BaseModel):
    value: float

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_float(self.value)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            value=des.get_float(),
        )


class InventoryItem(pydantic.BaseModel):
    name: str
    has_properties: bool
    type: str | None
    properties_size: int | None
    properties: "list[PropertyType] | None"

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_u32(0)
        ser.add_string(self.name)
        ser.add_u32_bool(self.has_properties)
        if self.has_properties:
            if self.type is not None:
                ser.add_string(self.type)
            if self.properties_size is not None:
                ser.add_u32(self.properties_size)
            if self.properties:
                for prop in self.properties:
                    ser.add(prop)  # type: ignore

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        from sat_sav_parse.models.properties import deserialize_properties  # noqa: PLC0415

        des.get_u32()
        name = des.get_string()
        has_properties = des.get_u32_bool()
        if has_properties:
            des.get_u32()
            _type = des.get_string()
            properties_size = des.get_u32()
            with expect_size(des, properties_size, "InventoryItem.properties"):
                properties = des.get_fn(deserialize_properties)
            return cls(
                name=name,
                has_properties=has_properties,
                type=_type,
                properties_size=properties_size,
                properties=properties,
            )
        return cls(
            name=name,
            has_properties=has_properties,
            type=None,
            properties_size=None,
            properties=None,
        )


class LinearColor(pydantic.BaseModel):
    r: float
    g: float
    b: float
    a: float

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_float(self.r)
        ser.add_float(self.g)
        ser.add_float(self.b)
        ser.add_float(self.a)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            r=des.get_float(),
            g=des.get_float(),
            b=des.get_float(),
            a=des.get_float(),
        )


class Quat(pydantic.BaseModel):
    x: float
    y: float
    z: float
    w: float

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_double(self.x)
        ser.add_double(self.y)
        ser.add_double(self.z)
        ser.add_double(self.w)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            x=des.get_double(),
            y=des.get_double(),
            z=des.get_double(),
            w=des.get_double(),
        )


class RailroadTrackPosition(pydantic.BaseModel):
    object_reference: ObjectReference
    offset: float
    forward: float

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add(self.object_reference)
        ser.add_float(self.offset)
        ser.add_float(self.forward)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            object_reference=des.get(ObjectReference),
            offset=des.get_float(),
            forward=des.get_float(),
        )


class Vector(pydantic.BaseModel):
    x: float
    y: float
    z: float

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_double(self.x)
        ser.add_double(self.y)
        ser.add_double(self.z)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            x=des.get_double(),
            y=des.get_double(),
            z=des.get_double(),
        )


class DateTime(pydantic.BaseModel):
    value: int

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_i64(self.value)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(value=des.get_i64())


class ClientIdentityInfoIdentityVariant(U8EnumSerializerMixin, U8EnumDeserializerMixin, enum.IntEnum):
    EPIC = 1
    STEAM = 6


class ClientIdentityInfoIdentity(pydantic.BaseModel):
    variant: ClientIdentityInfoIdentityVariant
    payload: pydantic.Base64Bytes

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add(self.variant)
        ser.add_u32(len(self.payload))
        ser.add_raw(self.payload)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        variant = des.get(ClientIdentityInfoIdentityVariant)
        data_size = des.get_u32()
        data = des.content[des.offset : des.offset + data_size]
        des.offset += data_size
        return cls(variant=variant, payload=b64_bytes(data))


class ClientIdentityInfo(pydantic.BaseModel):
    uuid: str
    identities: list[ClientIdentityInfoIdentity]

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.uuid)
        ser.add_u32(len(self.identities))
        for identity in self.identities:
            ser.add(identity)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            uuid=des.get_string(),
            identities=[des.get(ClientIdentityInfoIdentity) for _ in range(des.get_u32())],
        )


class SpawnData(pydantic.BaseModel):
    name: str
    type: typing.Literal["ObjectProperty"]
    size: int
    level_path: ObjectReference
    properties: "list[PropertyType]"

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        from sat_sav_parse.models.properties import deserialize_properties  # noqa: PLC0415

        name = des.get_string()
        _type = des.confirm_basic_type(des.parse_string, "ObjectProperty")
        size = des.get_u32()
        des.confirm_basic_type(des.parse_u32, 0)
        des.confirm_basic_type(des.parse_u8, 0)
        with expect_size(des, size, "SpawnData"):
            level_path = des.get(ObjectReference)
        properties = deserialize_properties(des)
        return cls(
            name=name,
            type=typing.cast('typing.Literal["ObjectProperty"]', _type),
            size=size,
            level_path=level_path,
            properties=properties,
        )


type StructValue = typing.Union[  # noqa: UP007
    LinearColor,
    SpawnData,
    Quat,
    Box,
    InventoryItem,
    FluidBox,
    RailroadTrackPosition,
    DateTime,
    ClientIdentityInfo,
    Vector,
    "list[PropertyType]",
]


@set_struct_name("StructValue")
def deserialize_struct_value(  # noqa: PLR0911
    des: "SFSaveDeserializer",
    struct_type: StructTypeName,
    payload_size: int,
) -> StructValue | pydantic.Base64Bytes:
    from sat_sav_parse.models.properties import deserialize_properties  # noqa: PLC0415

    match struct_type:
        case StructTypeName.LINEAR_COLOR | StructTypeName.COLOR:
            return des.get(LinearColor)
        case StructTypeName.VECTOR:
            return des.get(Vector)
        case StructTypeName.SPAWN_DATA:
            return des.get(SpawnData)
        case StructTypeName.VECTOR | StructTypeName.ROTATOR:
            return des.get(Vector)
        case StructTypeName.QUAT:
            return des.get(Quat)
        case StructTypeName.BOX:
            return des.get(Box)
        case StructTypeName.INVENTORY_ITEM:
            return des.get(InventoryItem)
        case StructTypeName.FLUID_BOX:
            return des.get(FluidBox)
        case StructTypeName.RAILROAD_TRACK_POSITION:
            return des.get(RailroadTrackPosition)
        case StructTypeName.DATE_TIME:
            return des.get(DateTime)
        case StructTypeName.CLIENT_IDENTITY_INFO:
            return des.get(ClientIdentityInfo)
        case StructTypeName.GUID:
            return des.get_item(payload_size)
        case _:
            start_offset = des.offset
            try:
                return des.get_fn(deserialize_properties)
            except (ParseError, ValueError):
                des.offset = start_offset
                logger.warning("Failed to deserialize struct type %s, returning raw bytes", struct_type)
                return des.get_item(payload_size)
