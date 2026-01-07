import functools
import logging
import typing

import pydantic

from sat_sav_parse.models.properties.base import BaseProperty
from sat_sav_parse.models.properties.enums import PropertyTypeName, StructTypeName
from sat_sav_parse.models.properties.typed_data import StructValue, deserialize_struct_value
from sat_sav_parse.utils import b64_bytes

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer

__all__ = ("StructProperty",)

logger = logging.getLogger(__name__)


class StructProperty(BaseProperty[StructValue | pydantic.Base64Bytes]):
    type_name: typing.Literal[PropertyTypeName.STRUCT] = PropertyTypeName.STRUCT
    index: int
    type: StructTypeName

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        name = des.get_string()
        des.get(PropertyTypeName)
        payload_size = des.get_u32()
        index = des.get_u32()
        element_type = des.get(StructTypeName)
        des.get_item(17)
        _, value = des.parse_item(des.offset, des.content, payload_size)

        value = des.get_fn(
            functools.partial(deserialize_struct_value, struct_type=element_type, payload_size=payload_size),
        )

        return cls(
            name=name,
            payload_size=payload_size,
            index=index,
            type=element_type,
            payload=b64_bytes(value),
        )
