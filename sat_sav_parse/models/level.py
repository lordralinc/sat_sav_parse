import functools
import typing

import pydantic

from sat_sav_parse.logger import set_struct_name
from sat_sav_parse.models.level_object import LevelObjectType, deserialize_level_object
from sat_sav_parse.models.object_header import ObjectHeaderType, deserialize_object_header, serialize_object_header
from sat_sav_parse.models.object_reference import ObjectReference
from sat_sav_parse.progress import LogProgress
from sat_sav_parse.utils import expect_size

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = ("Level",)


class Level(pydantic.BaseModel):
    sublevel_name: str | None
    object_header_and_collectables_size: int
    object_headers: list[ObjectHeaderType]
    extra_level_names_count: int | None
    extra_level_names: str | None
    collectables: list[ObjectReference]
    objects_size: int
    objects: list[LevelObjectType]
    save_version: int
    second_collectables: list[ObjectReference]

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        if self.sublevel_name is not None:
            ser.add_string(self.sublevel_name)
        ser.add_u64(self.object_header_and_collectables_size)
        ser.add_u32(len(self.object_headers))
        for object_header in self.object_headers:
            ser.add_fn(serialize_object_header, object_header)
        if self.extra_level_names_count is not None:
            ser.add_u32(self.extra_level_names_count)
        if self.extra_level_names is not None:
            ser.add_string(self.extra_level_names)
        ser.add_u32(len(self.collectables))
        for collectable in self.collectables:
            ser.add(collectable)
        ser.add_u64(len(self.objects))
        for obj in self.objects:
            ser.add(obj)
        ser.add_u32(self.save_version)
        ser.add_u32(len(self.second_collectables))
        for collectable in self.second_collectables:
            ser.add(collectable)


@set_struct_name("Level")
def deserialize_level(d: "SFSaveDeserializer", *, is_persistent: bool) -> Level:
    sublevel_name = d.get_string() if not is_persistent else None
    object_header_and_collectables_size = d.get_u64()
    object_header_and_collectable_start = d.offset
    object_header_count = d.get_u32()
    object_headers = [d.get_fn(deserialize_object_header) for _ in range(object_header_count)]

    extra_level_names_count = d.get_u32_bool() if is_persistent else None
    extra_level_names = d.get_string() if is_persistent and extra_level_names_count else None
    actual_size = d.offset - object_header_and_collectable_start

    if object_header_and_collectables_size != actual_size:
        collectables_count = d.get_u32()
        collectables = [d.get(ObjectReference) for _ in range(collectables_count)]
    else:
        collectables = []

    objects_size = d.get_u64()
    with expect_size(
        d,
        objects_size,
        "Level.objects",
    ):
        objects_count = d.get_u32()
        objects = [
            d.get_fn(functools.partial(deserialize_level_object, header=object_headers[idx]))
            for idx in (
                LogProgress.iter(
                    range(objects_count),
                    total=objects_count,
                    desc="persistent level objects",
                )
                if is_persistent
                else range(objects_count)
            )
        ]

    save_version = d.get_u32()

    if not is_persistent:
        second_collectables_count = d.get_u32()
        second_collectables = [d.get(ObjectReference) for _ in range(second_collectables_count)]
    else:
        second_collectables = []
    return Level(
        sublevel_name=sublevel_name,
        object_header_and_collectables_size=object_header_and_collectables_size,
        object_headers=object_headers,
        extra_level_names_count=extra_level_names_count,
        extra_level_names=extra_level_names,
        collectables=collectables,
        objects_size=objects_size,
        objects=objects,
        save_version=save_version,
        second_collectables=second_collectables,
    )
