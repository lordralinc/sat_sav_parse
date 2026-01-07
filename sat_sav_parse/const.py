import typing

TICKS_IN_SECOND: typing.Final[int] = 10 * 1000 * 1000
EPOCH_1_TO_1970: typing.Final[int] = 719162 * 24 * 60 * 60

SUPPORT_HEADER_TYPES: typing.Final[tuple[int, ...]] = (14,)
SUPPORT_SAVE_VERSIONS: typing.Final[tuple[int, ...]] = (52,)

MAX_CHUNK_SIZE: typing.Final[int] = 128 * 1024
TRACE_BIN_LOG_LEVEL: typing.Final[int] = 5
