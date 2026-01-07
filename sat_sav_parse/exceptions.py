import typing

type ParseErrorCode = typing.Literal[
    "unk",
    "invalid_flag",
    "unsupported_save_header_version",
    "unsupported_save_version",
    "invalid_file",
    "invalid_deserializer",
    "string_decode_failure",
    "invalid_size",
]


class ParseError(ValueError):
    code: ParseErrorCode
    message: str
    args: tuple[object, ...]

    @typing.overload
    def __init__(self, code: str, message: None = ..., *args: object) -> None: ...
    @typing.overload
    def __init__(self, code: ParseErrorCode, message: str, *args: object) -> None: ...

    def __init__(self, code: ParseErrorCode | str, message: str | None = None, *args: object) -> None:
        if message is None:
            msg = code.format(*args)
            code = "unk"
        else:
            msg = message.format(*args)
        super().__init__(msg)

        self.code = typing.cast("ParseErrorCode", code)
        self.message = msg
        self.args = args

    def __str__(self) -> str:
        return self.message.format(*self.args)

    def __repr__(self) -> str:
        code = self.code
        message = self.message.format(*self.args)
        return f"<ParseError {code=} {message=}>"
