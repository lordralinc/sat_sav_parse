import enum
import typing

import pydantic

from sat_sav_parse.logger import set_struct_name
from sat_sav_parse.utils import U32EnumDeserializerMixin, U32EnumSerializerMixin

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = (
    "ActorHeader",
    "ComponentHeader",
    "HeaderType",
    "ObjectHeaderType",
    "Quaternion",
    "Vector3",
    "deserialize_object_header",
    "serialize_object_header",
)


class Vector3(pydantic.BaseModel):
    x: float
    y: float
    z: float

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_float(self.x)
        ser.add_float(self.y)
        ser.add_float(self.z)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            x=des.get_float(),
            y=des.get_float(),
            z=des.get_float(),
        )


class Quaternion(pydantic.BaseModel):
    x: float
    y: float
    z: float
    w: float

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_float(self.x)
        ser.add_float(self.y)
        ser.add_float(self.z)
        ser.add_float(self.w)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            x=des.get_float(),
            y=des.get_float(),
            z=des.get_float(),
            w=des.get_float(),
        )


class HeaderType(U32EnumSerializerMixin, U32EnumDeserializerMixin, enum.IntEnum):
    COMPONENT = 0
    ACTOR = 1


class ActorHeader(pydantic.BaseModel):
    type: typing.Literal[HeaderType.ACTOR] = HeaderType.ACTOR
    type_path: typing.Annotated[
        str,
        pydantic.Field(title="Type Path", description="The type of actor, described in a hierarchical path"),
    ]
    root_object: typing.Annotated[
        str,
        pydantic.Field(title="Root Object"),
    ]
    instance_name: typing.Annotated[
        str,
        pydantic.Field(title="Instance Name", description="The unique name of this actor object"),
    ]
    unknown: typing.Annotated[
        int,
        pydantic.Field(title="Unknown Uint32"),
    ]
    rotation: Quaternion
    position: Vector3
    scale: Vector3

    need_transform: typing.Annotated[
        bool,
        pydantic.Field(title="Need Transform?", description="Seemingly a boolean flag; semantics unclear"),
    ]

    was_placed_in_level: typing.Annotated[
        bool,
        pydantic.Field(title="Was Placed In Level?", description="Seemingly a boolean flag; semantics unclear"),
    ]

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add(self.type)
        ser.add_string(self.type_path)
        ser.add_string(self.root_object)
        ser.add_string(self.instance_name)
        ser.add_u32(self.unknown)
        ser.add(self.rotation)
        ser.add(self.position)
        ser.add(self.scale)
        ser.add_u32_bool(self.need_transform)
        ser.add_u32_bool(self.was_placed_in_level)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            type_path=des.get_string(),
            root_object=des.get_string(),
            instance_name=des.get_string(),
            unknown=des.get_u32(),
            need_transform=des.get_u32_bool(),
            rotation=des.get(Quaternion),
            position=des.get(Vector3),
            scale=des.get(Vector3),
            was_placed_in_level=des.get_u32_bool(),
        )


class ComponentHeader(pydantic.BaseModel):
    type: typing.Literal[HeaderType.COMPONENT] = HeaderType.COMPONENT
    type_path: typing.Annotated[
        str,
        pydantic.Field(title="Type Path", description="The type of component, described in a hierarchical path"),
    ]
    root_object: typing.Annotated[
        str,
        pydantic.Field(title="Root Object"),
    ]
    instance_name: typing.Annotated[
        str,
        pydantic.Field(title="Instance Name", description="the name of this single component object "),
    ]
    unknown: typing.Annotated[
        int,
        pydantic.Field(title="Unknown Uint32"),
    ]
    parent_actor_name: typing.Annotated[
        str,
        pydantic.Field(title="parent actor name", description="a reference to the instance name of an actor"),
    ]

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add(self.type)
        ser.add_string(self.type_path)
        ser.add_string(self.root_object)
        ser.add_string(self.instance_name)
        ser.add_u32(self.unknown)
        ser.add_string(self.parent_actor_name)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            type_path=des.get_string(),
            root_object=des.get_string(),
            instance_name=des.get_string(),
            unknown=des.get_u32(),
            parent_actor_name=des.get_string(),
        )


type ObjectHeaderType = typing.Annotated[ActorHeader | ComponentHeader, pydantic.Field(discriminator="type")]


def serialize_object_header(ser: "SFSaveSerializer", obj: ObjectHeaderType) -> None:
    ser.add(obj)


@set_struct_name("ObjectHeader")
def deserialize_object_header(des: "SFSaveDeserializer") -> ObjectHeaderType:
    header_type = des.get(HeaderType)
    if header_type == HeaderType.COMPONENT:
        return des.get(ComponentHeader)
    if header_type == HeaderType.ACTOR:
        return des.get(ActorHeader)
    typing.assert_never(header_type)
