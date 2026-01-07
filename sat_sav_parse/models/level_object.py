import functools
import typing

import pydantic

from sat_sav_parse.logger import set_struct_name
from sat_sav_parse.models.object_header import ActorHeader, ComponentHeader, HeaderType, ObjectHeaderType
from sat_sav_parse.models.object_reference import ObjectReference
from sat_sav_parse.models.properties import PropertyType, deserialize_properties
from sat_sav_parse.utils import b64_bytes, expect_size

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = (
    "ActorObject",
    "ComponentObject",
    "LevelObjectType",
    "deserialize_level_object",
)


class ActorObject(pydantic.BaseModel):
    type: typing.Literal[HeaderType.ACTOR] = HeaderType.ACTOR
    header: ActorHeader
    save_version: int
    flag: int
    size: int
    parent_object_reference: ObjectReference
    components: list[ObjectReference]
    properties: list[PropertyType]
    trailing: pydantic.Base64Bytes  # TODO: КАЖЕТСЯ ЭТО ЧТО-ТО ЗНАЧИТ

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_u32(self.save_version)
        ser.add_u32(self.flag)
        ser.add_u32(self.size)
        ser.add(self.parent_object_reference)
        for component in self.components:
            ser.add(component)
        for prop in self.properties:
            ser.add(prop)
        ser.add_u32(0)
        ser.add_raw(self.trailing)

    @classmethod
    @set_struct_name("ActorObject")
    def deserialize_with_header(cls, des: "SFSaveDeserializer", header: ActorHeader) -> typing.Self:
        save_version = des.get_u32()
        flag = des.get_u32()
        size = des.get_u32()
        with expect_size(des, size, "ActorObject"):
            start_offset = des.offset
            parent_object_reference = des.get(ObjectReference)
            components = [des.get(ObjectReference) for _ in range(des.get_u32())]
            properties = des.get_fn(deserialize_properties)
            des.get_u32()
            remaining_size = size - (des.offset - start_offset)
            trailing = des.get_item(remaining_size)
        return cls(
            type=header.type,
            header=header,
            save_version=save_version,
            flag=flag,
            size=size,
            parent_object_reference=parent_object_reference,
            components=components,
            properties=properties,
            trailing=b64_bytes(trailing),  # type: ignore
        )


class ComponentObject(pydantic.BaseModel):
    type: typing.Literal[HeaderType.COMPONENT] = HeaderType.COMPONENT
    header: ComponentHeader
    save_version: int
    flag: int
    size: int
    properties: list[PropertyType]
    trailing: pydantic.Base64Bytes  # TODO: КАЖЕТСЯ ЭТО ЧТО-ТО ЗНАЧИТ

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_u32(self.save_version)
        ser.add_u32(self.flag)
        ser.add_u32(self.size)
        for prop in self.properties:
            ser.add(prop)
        ser.add_u32(0)
        ser.add_raw(self.trailing)

    @classmethod
    @set_struct_name("ComponentObject")
    def deserialize_with_header(cls, des: "SFSaveDeserializer", header: ComponentHeader) -> typing.Self:
        save_version = des.get_u32()
        flag = des.get_u32()
        size = des.get_u32()
        with expect_size(des, size, "ComponentObject"):
            start_offset = des.offset
            properties = des.get_fn(deserialize_properties)
            des.get_u32()
            trailing_size = size - (des.offset - start_offset)
            trailing = des.get_item(trailing_size)

        return cls(
            type=header.type,
            header=header,
            save_version=save_version,
            flag=flag,
            size=size,
            properties=properties,
            trailing=b64_bytes(trailing),  # type: ignore
        )


type LevelObjectType = typing.Annotated[ActorObject | ComponentObject, pydantic.Field(discriminator="type")]


@set_struct_name("LevelObject")
def deserialize_level_object(des: "SFSaveDeserializer", header: ObjectHeaderType) -> LevelObjectType:
    if header.type == HeaderType.ACTOR:
        return des.get_fn(functools.partial(ActorObject.deserialize_with_header, header=header))
    if header.type == HeaderType.COMPONENT:
        return des.get_fn(functools.partial(ComponentObject.deserialize_with_header, header=header))
    typing.assert_never(header.type)
