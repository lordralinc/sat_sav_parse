import argparse
import logging
import pathlib
import sys

from rich.logging import RichHandler
from rich_argparse import RichHelpFormatter

from sat_sav_parse import ContextFilter
from sat_sav_parse.cli.info import info_command
from sat_sav_parse.cli.to_json import to_json_command

RICH_FORMAT = "%(name)s%(context)s - %(message)s"

parser = argparse.ArgumentParser(description="Save file CLI", formatter_class=RichHelpFormatter)
parser.add_argument("--log-level", type=str, default="INFO", help="Set log level")
parser.add_argument("--disable-logging", action="store_true", help="Disable logging")
subparsers = parser.add_subparsers(dest="command", required=True)

parser_info = subparsers.add_parser("info", help="Show save info")
parser_info.add_argument("filename", type=pathlib.Path, help="Path to the save file")
parser_info.add_argument("--json", "-j", action="store_true", help="Show as JSON")
parser_info.add_argument("--plain", "-p", action="store_true", help="Disable indent and colors for JSON output")

parser_to_json = subparsers.add_parser("to-json", help="Save to JSON")
parser_to_json.add_argument("filename", type=pathlib.Path, help="Path to the save file")
parser_to_json.add_argument(
    "--output",
    "-o",
    type=pathlib.Path,
    required=False,
    help="Path to output JSON file; if not set, saved in {input}.json",
)
parser_to_json.add_argument(
    "--header",
    "-hf",
    type=pathlib.Path,
    required=False,
    help="Path to output header JSON file; if not set, header saved in {output}.header.json",
)


COMMANDS = {
    "info": info_command,
    "to-json": to_json_command,
}


def main():
    args = parser.parse_args()

    command_func = COMMANDS.get(args.command)
    if command_func is None:
        parser.print_help()
        sys.exit(1)
    kwargs = vars(args)
    kwargs.pop("command")

    if kwargs.pop("disable_logging"):
        logging.disable(logging.CRITICAL)
    else:
        log_level = kwargs.pop("log_level")
        context_filter = ContextFilter()

        console_handler = RichHandler(rich_tracebacks=True, tracebacks_show_locals=True, keywords=["TRACE_BIN"])
        console_handler.addFilter(context_filter)
        console_handler.setFormatter(logging.Formatter(RICH_FORMAT, datefmt="[%X]"))
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            datefmt="[%X]",
            handlers=[console_handler],
        )

    command_func(**kwargs)


if __name__ == "__main__":
    main()
