import enum
import typing

import pydantic

from sat_sav_parse.utils import StrEnumDeserializerMixin, StrEnumSerializerMixin

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = (
    "GridName",
    "LevelGroupingGrid",
    "LevelInfo",
)


class GridName(StrEnumSerializerMixin, StrEnumDeserializerMixin, enum.StrEnum):
    MAIN = "MainGrid"
    LANDSCAPE = "LandscapeGrid"
    EXPLORATION = "ExplorationGrid"
    FOLIAGE = "FoliageGrid"
    HLOD = "HLOD0_256m_1023m"


class LevelInfo(pydantic.BaseModel):
    name: typing.Annotated[str, pydantic.Field(title="Level Name", description="Name of the sublevel")]
    value: typing.Annotated[int, pydantic.Field(title="Level Value", description="Associated integer for the level")]

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.name)
        ser.add_u32(self.value)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(name=des.get_string(), value=des.get_u32())


class LevelGroupingGrid(pydantic.BaseModel):
    grid_name: typing.Annotated[GridName, pydantic.Field(title="Grid Name")]

    unknown_1: typing.Annotated[int, pydantic.Field(title="Unknown Uint32 #1", description="Purpose unclear")]
    unknown_2: typing.Annotated[int, pydantic.Field(title="Unknown Uint32 #2", description="Purpose unclear")]
    levels: typing.Annotated[
        list[LevelInfo],
        pydantic.Field(title="Level Info", description="List of level name + integer pairs"),
    ]

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add(self.grid_name)
        ser.add_u32(self.unknown_1)
        ser.add_u32(self.unknown_2)
        ser.add_u32(len(self.levels))
        for level in self.levels:
            ser.add(level)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            grid_name=des.get(GridName),
            unknown_1=des.get_u32(),
            unknown_2=des.get_u32(),
            levels=[des.get(LevelInfo) for _ in range(des.get_u32())],
        )
