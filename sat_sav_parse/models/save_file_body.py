import functools
import itertools
import logging
import typing

import pydantic

from sat_sav_parse.models.level import Level, deserialize_level
from sat_sav_parse.models.level_grouping_grid import LevelGroupingGrid
from sat_sav_parse.models.object_reference import ObjectReference
from sat_sav_parse.progress import LogProgress
from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = ("SaveFileBody",)

logger = logging.getLogger(__name__)


class SaveFileBody(pydantic.BaseModel):
    unknown_1: int
    unknown_2: int
    grids: typing.Annotated[list["LevelGroupingGrid"], pydantic.Field(min_length=5, max_length=5)]
    sublevels: list["Level"]
    persistent_level: "Level"
    references: list["ObjectReference"]

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ns = SFSaveSerializer()
        ns.add_u32(6)
        ns.add_string("None")
        ns.add_u32(0)
        ns.add_u32(self.unknown_1)
        ns.add_u32(1)
        ns.add_string("None")
        ns.add_u32(self.unknown_2)

        for grid in self.grids:
            ns.add(grid)

        ns.add_u32(len(self.sublevels))
        for lvl in itertools.chain(self.sublevels, [self.persistent_level]):
            ns.add(lvl)

        ns.add_u32(len(self.references))
        for ref in self.references:
            ns.add(ref)

        ser.add_u64(len(ns.content))
        ser.add_raw(ns.content)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        des.get_u64()
        des.get_u32()
        des.confirm_basic_type(des.parse_string, "None")
        des.confirm_basic_type(des.parse_u32, 0)

        unknown_1 = des.get_u32()
        des.confirm_basic_type(des.parse_u32, 1)
        des.confirm_basic_type(des.parse_string, "None")
        unknown_2 = des.get_u32()

        grids = [des.get(LevelGroupingGrid) for _ in range(5)]

        sublevel_count = des.get_u32()
        levels = LogProgress.iter_list(
            [des.get_fn(functools.partial(deserialize_level, is_persistent=False)) for _ in range(sublevel_count)],
            total=sublevel_count,
            desc="sublevels",
        )

        persistent_level = des.get_fn(functools.partial(deserialize_level, is_persistent=True))

        if des.offset == len(des.content):
            logger.warning("Missing final refs count")
            des.content += b"\x00\x00\x00\x00"

        ref_count = des.get_u32()
        refs = [des.get(ObjectReference) for _ in range(ref_count)]

        return cls(
            unknown_1=unknown_1,
            unknown_2=unknown_2,
            grids=grids,
            sublevels=levels,
            persistent_level=persistent_level,
            references=refs,
        )
