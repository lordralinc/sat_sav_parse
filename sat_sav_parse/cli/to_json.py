import pathlib

import rich

from sat_sav_parse import CSaveFileBody, SaveFileBody, SaveFileHeader, SFSaveDeserializer

console = rich.console.Console(record=True)


def to_json_command(
    filename: pathlib.Path,
    output: pathlib.Path | None = None,
    header: pathlib.Path | None = None,
) -> None:
    if not filename.exists():
        console.print(f"File {filename} does not exist", style="bold red")
        return
    output = output or filename.with_suffix(".json")
    header = header or output.with_suffix(".header.json")

    try:
        file = filename.read_bytes()
        des = SFSaveDeserializer(file)

        file_info = des.get(SaveFileHeader)
        header.write_text(file_info.model_dump_json(indent=2))
        console.print(f"Header saved to {header}", style="bold green")

        decompressed = des.get(CSaveFileBody)
        dec_des = SFSaveDeserializer(decompressed)
        file_body = dec_des.get(SaveFileBody)
        output.write_text(file_body.model_dump_json(indent=2))
        console.print(f"Save body saved to {output}", style="bold green")
    except Exception as e:  # noqa: BLE001
        console.print(f"Failed to read file {filename}: {e}", style="bold red")
        return
