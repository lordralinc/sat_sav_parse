import typing

import pydantic

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = ("ObjectReference",)


class ObjectReference(pydantic.BaseModel):
    level_name: str
    path_name: str

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_string(self.level_name)
        ser.add_string(self.path_name)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        return cls(
            level_name=des.get_string(),
            path_name=des.get_string(),
        )

    def __hash__(self) -> int:
        return hash((self.level_name, self.path_name))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ObjectReference):
            return False
        return self.level_name == other.level_name and self.path_name == other.path_name
