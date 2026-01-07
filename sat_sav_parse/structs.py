import collections
import collections.abc
import logging
import struct
import typing

from sat_sav_parse.const import TRACE_BIN_LOG_LEVEL
from sat_sav_parse.exceptions import ParseError
from sat_sav_parse.logger import get_struct_name, logging_with_context, repr_result

__all__ = (
    "SFSaveDeserializable",
    "SFSaveDeserializeFn",
    "SFSaveDeserializer",
    "SFSaveSerializable",
    "SFSaveSerializeFn",
    "SFSaveSerializer",
)


logger = logging.getLogger(__name__)


@typing.runtime_checkable
class SFSaveSerializable(typing.Protocol):
    def __serialize__(self, ser: "SFSaveSerializer") -> None: ...


type SFSaveSerializeFn[T] = collections.abc.Callable[["SFSaveSerializer", T], None]


@typing.runtime_checkable
class SFSaveDeserializable(typing.Protocol):
    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self: ...


type SFSaveDeserializeFn[T] = collections.abc.Callable[["SFSaveDeserializer"], T]


class SFSaveSerializer:
    def __init__(self, init_content: bytes | None = None) -> None:
        self.content = init_content or b""
        logger.log(TRACE_BIN_LOG_LEVEL, "Serializator init size=%d", len(self.content))

    def add(self, s: SFSaveSerializable) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "serialize object %s", type(s).__qualname__)
        before = len(self.content)
        s.__serialize__(self)
        logger.log(
            TRACE_BIN_LOG_LEVEL,
            "serialize object %s done: +%d bytes",
            type(s).__qualname__,
            len(self.content) - before,
        )
        return self

    def add_fn[T](self, fn: SFSaveSerializeFn[T], obj: T) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "serialize fn %s(%r)", fn.__qualname__, obj)
        before = len(self.content)
        fn(self, obj)
        logger.log(
            TRACE_BIN_LOG_LEVEL,
            "serialize fn %s done: +%d bytes",
            fn.__qualname__,
            len(self.content) - before,
        )
        return self

    def add_raw(self, value: bytes) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_raw %d bytes", len(value))
        self.content += value
        return self

    def add_i8(self, value: int) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_i8 %d", value)
        self.content += struct.pack("<b", value)
        return self

    def add_i32(self, value: int) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_i32 %d", value)
        self.content += struct.pack("<i", value)
        return self

    def add_i64(self, value: int) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_i64 %d", value)
        self.content += struct.pack("<q", value)
        return self

    def add_u8(self, value: int) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_u8 %d", value)
        self.content += struct.pack("<B", value)
        return self

    def add_u32(self, value: int) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_u32 %d", value)
        self.content += struct.pack("<I", value)
        return self

    def add_u64(self, value: int) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_u64 %d", value)
        self.content += struct.pack("<Q", value)
        return self

    def add_float(self, value: float) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_float %f", value)
        self.content += struct.pack("<f", value)
        return self

    def add_double(self, value: float) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_double %f", value)
        self.content += struct.pack("<d", value)
        return self

    def add_u8_bool(self, value: bool) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_u8_bool %s", value)
        return self.add_u8(int(value))

    def add_u32_bool(self, value: bool) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_u32_bool %s", value)
        return self.add_u32(int(value))

    def add_string(self, value: str) -> typing.Self:
        logger.log(TRACE_BIN_LOG_LEVEL, "add_string %r", value)

        if not value:
            self.content += struct.pack("<i", 0)
            return self

        try:
            encoded = value.encode("utf-8")
            length = len(encoded) + 1
            logger.log(TRACE_BIN_LOG_LEVEL, "string utf-8 bytes=%d", length)
            self.content += struct.pack("<i", length) + encoded + b"\x00"
        except UnicodeEncodeError:
            encoded = value.encode("utf-16-le")
            char_count = (len(encoded) // 2) + 1
            logger.log(TRACE_BIN_LOG_LEVEL, "string utf-16 chars=%d", char_count)
            self.content += struct.pack("<i", -char_count) + encoded + b"\x00\x00"

        return self

    @classmethod
    def get(cls, s: SFSaveSerializable) -> bytes:
        ser = cls()
        ser.add(s)  # type: ignore
        return ser.content

    @classmethod
    def get_fn[T](cls, fn: SFSaveSerializeFn[T], obj: T | None = None) -> bytes:
        ser = cls()
        ser.add_fn(fn, obj)  # type: ignore
        return ser.content


class SFSaveDeserializer:
    def __init__(self, data: bytes, offset: int = 0):
        self.content = data
        self.offset = offset
        logger.log(
            TRACE_BIN_LOG_LEVEL,
            "Deserializer init size=%d offset=%d",
            len(data),
            offset,
        )

    def get[T: SFSaveDeserializable](self, item: type[T]) -> T:
        with logging_with_context(struct=item.__name__, offset=self.offset):
            start = self.offset
            value = item.__deserialize__(self)

            if self.offset == start:
                logger.error(
                    TRACE_BIN_LOG_LEVEL,
                    "Deserializer %s did not advance offset (%d)",
                    item.__qualname__,
                    start,
                )
                raise ParseError(
                    "invalid_deserializer",
                    "Deserializer did not advance offset",
                )

            logger.log(
                TRACE_BIN_LOG_LEVEL,
                "GET                of[%10d -> %-10d] %7s | %s",
                start,
                self.offset,
                get_struct_name(item),
                repr_result(value),
            )
            return value

    def get_fn[T](self, fn: SFSaveDeserializeFn[T]) -> T:
        with logging_with_context(struct=fn, offset=self.offset):
            start_offset = self.offset
            value = fn(self)
            logger.log(
                TRACE_BIN_LOG_LEVEL,
                "GET FUNCTION       of[%10d -> %-10d] %7s | %s",
                start_offset,
                self.offset,
                get_struct_name(fn),
                repr_result(value),
            )
            return value

    def get_item[T](
        self,
        data_len: int,
        unpack_flag: str | None = None,
        item_type: collections.abc.Callable[[typing.Any], T] = lambda x: x,
    ) -> T:
        start_offset = self.offset
        self.offset, data = self.parse_item(
            self.offset,
            self.content,
            data_len,
            unpack_flag,
            item_type,
        )
        logger.log(
            TRACE_BIN_LOG_LEVEL,
            "GET ITEM           of[%10d -> %-10d] %7s | %s",
            start_offset,
            self.offset,
            unpack_flag or "raw",
            repr_result(data),
        )
        return data

    def get_i8(self) -> int:
        old = self.offset
        self.offset, v = self.parse_i8(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET I8             of[%10d -> %-10d] | %d", old, self.offset, v)
        return v

    def get_i32(self) -> int:
        old = self.offset
        self.offset, v = self.parse_i32(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET I32            of[%10d -> %-10d] | %d", old, self.offset, v)
        return v

    def get_i64(self) -> int:
        old = self.offset
        self.offset, v = self.parse_i64(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET I64            of[%10d -> %-10d] | %d", old, self.offset, v)
        return v

    def get_u8(self) -> int:
        old = self.offset
        self.offset, v = self.parse_u8(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET U8             of[%10d -> %-10d] | %d", old, self.offset, v)
        return v

    def get_u32(self) -> int:
        old = self.offset
        self.offset, v = self.parse_u32(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET U32            of[%10d -> %-10d] | %d", old, self.offset, v)
        return v

    def get_u64(self) -> int:
        old = self.offset
        self.offset, v = self.parse_u64(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET U64            of[%10d -> %-10d] | %d", old, self.offset, v)
        return v

    def get_float(self) -> float:
        old = self.offset
        self.offset, v = self.parse_float(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET FLOAT          of[%10d -> %-10d] | %f", old, self.offset, v)
        return v

    def get_double(self) -> float:
        old = self.offset
        self.offset, v = self.parse_double(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET DOUBLE         of[%10d -> %-10d] | %f", old, self.offset, v)
        return v

    def get_u8_bool(self) -> bool:
        value = self.get_u8()
        if value not in (0, 1):
            logger.error("invalid u8 bool %d at offset=%d", value, self.offset - 1)
            raise ParseError("invalid_flag", "Flag value is {}. Valid values: {}", value, (0, 1))
        return bool(value)

    def get_u32_bool(self) -> bool:
        value = self.get_u32()
        if value not in (0, 1):
            logger.error("invalid u32 bool %d at offset=%d", value, self.offset - 4)
            raise ParseError("invalid_flag", "Flag value is {}. Valid values: {}", value, (0, 1))
        return bool(value)

    def get_string(self) -> str:
        old = self.offset
        self.offset, s = self.parse_string(self.offset, self.content)
        logger.log(TRACE_BIN_LOG_LEVEL, "GET STRING         of[%10d -> %-10d] | '%s'", old, self.offset, s)
        return s

    # ==================================================================
    # static parsing helpers
    # ==================================================================

    @classmethod
    def parse[T: SFSaveDeserializable](cls, offset: int, data: bytes, item: type[T]) -> T:
        return cls(data, offset).get(item)

    @classmethod
    def parse_fn[T](cls, offset: int, data: bytes, fn: SFSaveDeserializeFn[T]) -> T:
        return cls(data, offset).get_fn(fn)

    @classmethod
    def parse_item[T](
        cls,
        offset: int,
        data: bytes,
        data_len: int,
        unpack_flag: str | None = None,
        item_type: collections.abc.Callable[[typing.Any], T] = lambda x: x,
    ) -> tuple[int, T]:
        next_offset = offset + data_len

        logger.log(
            TRACE_BIN_LOG_LEVEL,
            "PARSE ITEM START   of[%10d -> %-10d] | '%s'",
            offset,
            offset + data_len,
            unpack_flag or "raw",
        )

        if next_offset > len(data):
            logger.error(
                "parse_item overflow offset=%d len=%d data_size=%d",
                offset,
                data_len,
                len(data),
            )
            raise ParseError(f"Offset {offset} too large in {len(data)}-byte data.")

        raw = data[offset:next_offset]
        value = struct.unpack(unpack_flag, raw)[0] if unpack_flag else raw
        value = item_type(value)

        logger.log(
            TRACE_BIN_LOG_LEVEL,
            "PARSE ITEM END     of[%10d -> %-10d] | '%s'",
            offset,
            next_offset,
            repr_result(value),
        )
        return next_offset, value

    @classmethod
    def parse_i8(cls, offset: int, data: bytes) -> tuple[int, int]:
        return cls.parse_item(offset, data, 1, "<b")

    @classmethod
    def parse_i32(cls, offset: int, data: bytes) -> tuple[int, int]:
        return cls.parse_item(offset, data, 4, "<i")

    @classmethod
    def parse_i64(cls, offset: int, data: bytes) -> tuple[int, int]:
        return cls.parse_item(offset, data, 8, "<q")

    @classmethod
    def parse_u8(cls, offset: int, data: bytes) -> tuple[int, int]:
        return cls.parse_item(offset, data, 1, "<B")

    @classmethod
    def parse_u32(cls, offset: int, data: bytes) -> tuple[int, int]:
        return cls.parse_item(offset, data, 4, "<I")

    @classmethod
    def parse_u64(cls, offset: int, data: bytes) -> tuple[int, int]:
        return cls.parse_item(offset, data, 8, "<Q")

    @classmethod
    def parse_float(cls, offset: int, data: bytes) -> tuple[int, float]:
        return cls.parse_item(offset, data, 4, "<f")

    @classmethod
    def parse_double(cls, offset: int, data: bytes) -> tuple[int, float]:
        return cls.parse_item(offset, data, 8, "<d")

    @classmethod
    def parse_string(cls, offset: int, data: bytes) -> tuple[int, str]:
        start = offset
        offset, string_len = cls.parse_i32(offset, data)

        logger.log(
            TRACE_BIN_LOG_LEVEL,
            "PARSE STRING START of[%10d -> %-10d]",
            start,
            start + string_len,
        )

        if string_len == 0:
            logger.log(
                TRACE_BIN_LOG_LEVEL,
                "PARSE STRING END   of[%10d -> %-10d] | '%s'",
                start,
                start + string_len,
                "",
            )
            return offset, ""

        if len(data) < offset + abs(string_len):
            logger.error(
                "string overflow len=%d offset=%d data_size=%d",
                string_len,
                offset,
                len(data),
            )
            raise ParseError(f"String length too large, size {string_len} at offset {offset - 4}.")

        try:
            if string_len > 0:
                raw = data[offset : offset + string_len - 1]
                s = raw.decode("utf-8", errors="strict")
                new_offset = offset + string_len
            else:
                raw = data[offset : offset - string_len * 2 - 2]
                s = raw.decode("utf-16-le")
                new_offset = offset + (-string_len * 2)

            logger.log(TRACE_BIN_LOG_LEVEL, "PARSE STRING END   of[%10d -> %-10d] | '%s'", start, start + string_len, s)

        except UnicodeDecodeError as exc:
            logger.exception(
                "string decode failed offset=%d len=%d",
                offset,
                string_len,
            )
            raise ParseError(
                "string_decode_failure",
                "String decode failure at offset {} of length {}",
                offset,
                string_len,
            ) from exc
        else:
            return new_offset, s

    def confirm_basic_type[T](
        self,
        parser: collections.abc.Callable[[int, bytes], tuple[int, T]],
        expected_value: T,
    ) -> T:
        self.offset, value = parser(self.offset, self.content)
        if value != expected_value:
            parser_name = get_struct_name(parser)
            raise ParseError(
                f"Value does not match the expected value. Parser: {parser_name} {value=!r} {expected_value=!r}",
            )
        return value
