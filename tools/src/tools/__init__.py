"""
    @file __init__.py
    
    Maybe `doxygen` just recognizes the triple-quotes.
"""

# print("Initializing tools...")

# import json
import os
from pathlib import Path
import tomllib
# from pprint import pprint as pp

from ._git_tools import get_upstream_url
from ._last_saved_date import last_saved_datetime as LSD

# print(f"Current working directory: {Path.cwd()}")

# DATA_FILE = Path("tools/source/data/tools.json")
# with DATA_FILE.open() as f:
#     DATA = json.load(f)

# pp(DATA)

CWD = Path.cwd()
if CWD.stem == 'lab':
    os.chdir('../')
# print(f Path.cwd())

with open("tools/pyproject.toml", "rb") as f:
    DATA = tomllib.load(f)["project"]

__doc__ = f"""{DATA["description"]}.


========== ⚠️  WARNING! ⚠️  ==========

This project is currently under construction.
Stay tuned for updates.

## Version

{DATA["version"]}

## Author

{DATA["authors"][0]["name"]}

## Date

{LSD(__file__).date()}

## Usage

### Jupyter
```python
from tools.glob4meson import glob4meson as g4m
g4m()
```

### Terminal
From the project directory:
```bash
bin/g4m
```

### Script
The intended usage. Call just before building objects or executables.
@see Terminal. 

## System Requirements



@see [GitHub]({get_upstream_url()})

"""

BASE = Path.cwd()

# from .glob4meson.glob4meson import glob4meson as g4m

# from .build import *
from .constants import *
# from .devel import *
from .nbtools import *
# from .read_lines import *
print("Initialized `tools` package")
print(f"{FOLDER_PICT} Current directory: {Path.cwd().name}")