import logging
import typing
import zlib

from sat_sav_parse.const import MAX_CHUNK_SIZE
from sat_sav_parse.exceptions import ParseError

if typing.TYPE_CHECKING:
    from sat_sav_parse.structs import SFSaveDeserializer, SFSaveSerializer

logger = logging.getLogger(__name__)

__all__ = ("CSaveFileBody", "CSaveFileChunk")


class CSaveFileChunk(bytes):
    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        ser.add_u32(0x9E2A83C1)
        ser.add_u32(0x22222222)
        ser.add_u8(0)
        ser.add_u32(MAX_CHUNK_SIZE)
        ser.add_u32(0x03000000)

        compressed = zlib.compress(self)
        compressed_size = len(compressed)
        uncompressed_size = len(self)

        ser.add_u64(compressed_size)
        ser.add_u64(uncompressed_size)
        ser.add_u64(compressed_size)
        ser.add_u64(uncompressed_size)
        ser.add_raw(compressed)

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        des.confirm_basic_type(des.parse_u32, 0x9E2A83C1)
        des.confirm_basic_type(des.parse_u32, 0x22222222)
        des.confirm_basic_type(des.parse_u8, 0)
        des.get_u32()
        des.confirm_basic_type(des.parse_u32, 0x03000000)

        compressed_size = des.get_u64()
        uncompressed_size = des.get_u64()

        if compressed_size != des.get_u64():
            raise ParseError("invalid_file", "Compressed size mismatch")
        if uncompressed_size != des.get_u64():
            raise ParseError("invalid_file", "Uncompressed size mismatch")

        result = zlib.decompress(des.content[des.offset : des.offset + compressed_size])
        des.offset += compressed_size

        if len(result) != uncompressed_size:
            raise ParseError("invalid_file", "Uncompressed size mismatch")

        return cls(result)


class CSaveFileBody(bytes):
    def __serialize__(self, ser: "SFSaveSerializer") -> None:
        data = memoryview(self)
        total_chunks = (len(data) + MAX_CHUNK_SIZE - 1) // MAX_CHUNK_SIZE

        logger.info("Serializing save body (%d chunks)", total_chunks)

        for i in range(0, len(data), MAX_CHUNK_SIZE):
            ser.add(CSaveFileChunk(data[i : i + MAX_CHUNK_SIZE]))

        logger.info("Serialization complete")

    @classmethod
    def __deserialize__(cls, des: "SFSaveDeserializer") -> typing.Self:
        chunks: list[bytes] = []
        total_size = len(des.content)

        logger.info("Deserializing save body")
        while des.offset < total_size:
            chunks.append(des.get(CSaveFileChunk))

        logger.info(
            "Deserialization complete (%d chunks, %d bytes)",
            len(chunks),
            sum(len(c) for c in chunks),
        )

        return cls(b"".join(chunks))
