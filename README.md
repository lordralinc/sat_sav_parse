# Satisfactory Save Parser

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Game](https://img.shields.io/badge/Game-Satisfactory-orange)

A collection of Python tools for parsing **Satisfactory** save files, as well as
displaying and manipulating their contents.

Supported Satisfactory versions:
**v1.1.1.6, v1.1.1.7, v1.1.2.0, v1.1.2.1, v1.1.2.2**

_[Satisfactory](https://www.satisfactorygame.com/) is a non-competitive,
first-person, open-world factory-building and exploration game developed by
[Coffee Stain Studios](https://www.coffeestain.com/)._

## Table of Contents

- **[Environment Variables](#environment-variables)**
- **[Command-Line Interface (CLI)](#command-line-interface-cli)**
- **[Using as a Library](#using-as-a-library)**
- **[Development & Architecture](#development--architecture)**
- **[Credits & Thanks](#credits--thanks)**

## Environment Variables

- **`SF_PROGRESS_USE_RICH`** - Enables Rich-based progress bars.
  Default: `1`

- **`SF_PROGRESS_LOG_EVERY`** - Controls how often progress information is printed to the console.
  Effective only when `SF_PROGRESS_USE_RICH` is set to `0`.
  Default: `100`

## Command-Line Interface (CLI)

## Using as a Library

## Development & Architecture

```tree
.
│   const.py           # Project constants
│   exceptions.py      # Custom exceptions
│   logger.py          # Logging setup
│   progress.py        # Progress bars
│   structs.py         # Struct (de)serializer
│   utils.py           # Utility/helper functions
│
├───cli                # Command-line interface (argument parsers and commands)
└───models             # Data models (Pydantic / structured data)

```

## Credits & Thanks

The source code in this repository was originally developed by
[GreyHak](https://github.com/GreyHak).

Source code credit for the quaternion/euler rotation conversions used by
`sav_cli.py` goes to
[Addison Sears-Collins](https://automaticaddison.com).

Special thanks to **[AnthorNet](https://github.com/AnthorNet)**, creator of the
[Satisfactory Calculator Interactive Map](https://satisfactory-calculator.com/en/interactive-map).

- The map used by `sav_to_html.py` is a modified version of the map extracted
  from Anthor's Interactive Map.
- Resource purities (defined in `sav_parse.py` as `RESOURCE_PURITY`) were
  extracted from the Interactive Map.
- Anthor's
  [pre-Update-8 JavaScript implementation](https://github.com/AnthorNet/SC-InteractiveMap/blob/dev/src/SaveParser/Read.js)
  was used as a reference.
- The Interactive Map was also used extensively to validate save files produced
  by `sav_to_resave.py` and `sav_cli.py`.

Thanks to the authors of the Satisfactory Wiki who documented the older but still
valuable v0.6.1.3 save file format at
[Satisfactory GG Wiki – Save File Format](https://satisfactory.wiki.gg/wiki/Save_files#Save_file_format).

The wiki was later updated for v1.0.0.4 using insights gained during the
development of these tools.

Additional thanks to the following contributors for sharing save files, enabling
expanded format support:

- [robison4th](https://github.com/robison4th)
- [JP Eagles and Katz](https://www.youtube.com/channel/UCgIwAJga0I6i68bWfwPdj1w)
- [Buggy](https://github.com/Buggy123)
- [Tomtores](https://github.com/Tomtores)
- [Mattigins](https://steamcommunity.com/profiles/76561198081088435)
- [TheRealBeef](https://github.com/TheRealBeef)
