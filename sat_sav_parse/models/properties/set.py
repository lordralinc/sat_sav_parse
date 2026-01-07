import enum
import logging
import typing

import pydantic

from sat_sav_parse.models.properties.array import ObjectReference
from sat_sav_parse.models.properties.base import BaseProperty
from sat_sav_parse.models.properties.enums import PropertyTypeName
from sat_sav_parse.utils import StrEnumDeserializerMixin, StrEnumSerializerMixin, b64_bytes, expect_size

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer


__all__ = (
    "SetProperty",
    "SetType",
)

logger = logging.getLogger()


class SetType(StrEnumSerializerMixin, StrEnumDeserializerMixin, enum.StrEnum):
    U_INT_32 = "UInt32Property"
    STRUCT = "StructProperty"
    OBJECT = "ObjectProperty"


class SetProperty(BaseProperty[list[ObjectReference] | list[int] | list[tuple[int, int]] | pydantic.Base64Bytes]):
    type_name: typing.Literal[PropertyTypeName.SET] = PropertyTypeName.SET
    set_type: SetType
    index: int

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        set_type = des.get(SetType)
        des.get_u8()
        with expect_size(des, payload_size, "SetProperty"):
            des.get_u32()
            length = des.get_u32()

            _, value_bytes = des.parse_item(des.offset, des.content, payload_size)
            values = []
            for _ in range(length):
                match set_type:
                    case SetType.OBJECT:
                        values.append(des.get(ObjectReference))
                    case SetType.U_INT_32:
                        values.append(des.get_u32())
                    case SetType.STRUCT:
                        values.append((des.get_u64(), des.get_u64()))
                    case _:
                        logger.warning("Deserializer for set element with type %r not found", set_type)
                        des.get_item(payload_size)
                        break

            return cls(
                name=name,
                payload_size=payload_size,
                set_type=set_type,
                index=index,
                payload=values or b64_bytes(value_bytes),
            )
