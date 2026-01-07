import pytest

from sat_sav_parse.exceptions import ParseError
from sat_sav_parse.structs import SFSaveDeserializer
from sat_sav_parse.utils import expect_size


def test_expect_size():
    size = 4
    content = b"\x00\x00\x00\x31\x00\x00\x00\x00"

    des = SFSaveDeserializer(content)

    with expect_size(des, size, "test"):
        des.get_u32()

    des = SFSaveDeserializer(content)

    with pytest.raises(ParseError), expect_size(des, size - 1, "test"):
        des.get_u32()
