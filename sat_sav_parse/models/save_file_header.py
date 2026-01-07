import datetime
import enum
import typing

import pydantic

from sat_sav_parse.const import EPOCH_1_TO_1970, SUPPORT_HEADER_TYPES, SUPPORT_SAVE_VERSIONS, TICKS_IN_SECOND
from sat_sav_parse.exceptions import ParseError
from sat_sav_parse.models.level_object import b64_bytes
from sat_sav_parse.utils import U8EnumDeserializerMixin, U8EnumSerializerMixin

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

__all__ = ("SaveFileHeader", "SessionVisibility")


class SessionVisibility(U8EnumSerializerMixin, U8EnumDeserializerMixin, enum.IntEnum):
    PRIVATE = 0
    FRIENDS_ONLY = 1


class SaveFileHeader(pydantic.BaseModel):
    header_type: typing.Annotated[int, pydantic.Field(description="save header version")]
    save_version: typing.Annotated[int, pydantic.Field(description="save version")]
    build_version: typing.Annotated[int, pydantic.Field(description="build version")]
    save_name: typing.Annotated[str, pydantic.Field(description="save name")]
    map_name: str
    map_options: str
    session_name: str
    play_duration: int
    save_ticks: int
    session_visibility: SessionVisibility
    editor_object_version: int
    mod_metadata: str
    mod_flags: int
    save_id: str
    is_partitioned_world: bool
    creative_mode_enabled: bool
    checksum: pydantic.Base64Bytes
    is_cheat: bool

    @property
    def play_timedelta(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=self.play_duration)

    @property
    def save_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.save_ticks / TICKS_IN_SECOND - EPOCH_1_TO_1970)

    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        (
            ser.add_u32(self.header_type)
            .add_u32(self.save_version)
            .add_u32(self.build_version)
            .add_string(self.save_name)
            .add_string(self.map_name)
            .add_string(self.map_options)
            .add_string(self.session_name)
            .add_u32(self.play_duration)
            .add_u64(self.save_ticks)
            .add(self.session_visibility)
            .add_u32(self.editor_object_version)
            .add_string(self.mod_metadata)
            .add_u32(self.mod_flags)
            .add_string(self.save_id)
            .add_u32_bool(self.is_partitioned_world)
            .add_u32_bool(self.creative_mode_enabled)
            .add_raw(self.checksum)
            .add_u32_bool(self.is_cheat)
        )

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        header_type = des.get_u32()
        if header_type not in SUPPORT_HEADER_TYPES:
            raise ParseError(
                "unsupported_save_header_version",
                "Unsupported save header version number {}",
                header_type,
            )
        save_version = des.get_u32()
        if save_version not in SUPPORT_SAVE_VERSIONS:
            raise ParseError(
                "unsupported_save_version",
                "Unsupported save version number {}",
                header_type,
            )
        build_version = des.get_u32()
        save_name = des.get_string()
        map_name = des.get_string()
        map_options = des.get_string()
        session_name = des.get_string()
        play_duration = des.get_u32()
        save_ticks = des.get_u64()
        session_visibility = des.get(SessionVisibility)
        editor_object_version = des.get_u32()
        mod_metadata = des.get_string()
        mod_flags = des.get_u32()
        persistent_save_id = des.get_string()
        is_partitioned_world = des.get_u32_bool()
        creative_mode_enabled = des.get_u32_bool()
        checksum = des.get_item(16)
        is_cheat = des.get_u32_bool()

        return cls(
            header_type=header_type,
            save_version=save_version,
            build_version=build_version,
            save_name=save_name,
            map_name=map_name,
            map_options=map_options,
            session_name=session_name,
            play_duration=play_duration,
            save_ticks=save_ticks,
            session_visibility=session_visibility,
            editor_object_version=editor_object_version,
            mod_metadata=mod_metadata,
            mod_flags=mod_flags,
            save_id=persistent_save_id,
            is_partitioned_world=is_partitioned_world,
            creative_mode_enabled=creative_mode_enabled,
            checksum=b64_bytes(checksum),  # type: ignore
            is_cheat=is_cheat,
        )
