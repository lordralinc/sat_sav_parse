import collections
import collections.abc
import contextlib
import contextvars
import functools
import inspect
import logging
import typing

from sat_sav_parse.const import TRACE_BIN_LOG_LEVEL

__all__ = (
    "ContextFilter",
    "disable_logging_hell",
    "enable_logging_hell",
    "logging_with_context",
    "prepare_logging_hell",
)

_log_context: contextvars.ContextVar[dict[str, typing.Any]] = contextvars.ContextVar(
    "log_context",
    default=dict(),  # noqa: B039
)

PS = typing.ParamSpec("PS")
R = typing.TypeVar("R")


def set_struct_name(
    name: str,
) -> collections.abc.Callable[[collections.abc.Callable[PS, R]], collections.abc.Callable[PS, R]]:
    def wrapper(fn: collections.abc.Callable[PS, R]) -> collections.abc.Callable[PS, R]:
        setattr(fn, "__struct_name__", name)  # noqa: B010
        return fn

    return wrapper


def get_struct_name(item: str | typing.Callable | functools.partial | typing.Any) -> str:  # noqa: PLR0911
    if hasattr(item, "__struct_name__"):
        return getattr(item, "__struct_name__", repr(item))

    if isinstance(item, str):
        return item
    if isinstance(item, functools.partial):
        return get_struct_name(item.func)
    if inspect.isclass(item):
        return item.__name__

    if hasattr(item, "__qualname__"):
        return getattr(item, "__qualname__", repr(item))
    if hasattr(item, "__name__"):
        return getattr(item, "__name__", repr(item))
    return repr(item)


def repr_result(result: typing.Any) -> str:
    if isinstance(result, bytes):
        return result.hex(" ")
    return repr(result)


@contextlib.contextmanager
def logging_with_context(**kwargs: typing.Any):
    current = _log_context.get()
    merged = current.copy()

    for k, v in kwargs.items():
        if k == "struct" and "struct" in merged:
            merged["struct"] = f"{merged['struct']}->'{get_struct_name(v)}'"
        else:
            merged[k] = f"'{v}'"

    token = _log_context.set(merged)
    try:
        yield
    finally:
        _log_context.reset(token)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        context = _log_context.get()
        record._ctx = context  # noqa: SLF001
        if context:
            record.context = " [{}]".format(" ".join([f"{k}={v}" for k, v in context.items()]))
        else:
            record.context = ""
        return True


def prepare_logging_hell():
    logging.addLevelName(TRACE_BIN_LOG_LEVEL, "TRACE_BIN")


def enable_logging_hell():
    for h in logging.getLogger().handlers:
        h.setLevel(TRACE_BIN_LOG_LEVEL)
    root = logging.getLogger()
    root.setLevel(TRACE_BIN_LOG_LEVEL)


def disable_logging_hell():
    for h in logging.getLogger().handlers:
        h.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
