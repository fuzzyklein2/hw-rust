###############################################################################
#   
#   NOTEBOOK TOOLS
#   
###############################################################################
from datetime import datetime as dt
from functools import singledispatch
import inspect
import os
from pathlib import Path
from pprint import pprint as pp
import sys

from grep import grep
from IPython.display import display, Markdown
import nbformat
import pyperclip
from rich import print as rp
from rich.columns import Columns
from rich.console import Console

from tools import *

###############################################################################
#   
#   Docstring
#   
###############################################################################
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
from tools import *
```

### Terminal
From the project directory:
```bash
python -m tools.constants
```

### Notebooks

## System Requirements



@see [GitHub]({get_upstream_url()})

"""

from .constants import *

###############################################################################
#   
#   LOGGING
#   
###############################################################################
def error(s:str):
    """ Print an error message.

        :param s: The message to print.
    """
    rp(ERROR_PICT + '[red]ERROR[/red]: ' + s)

def warn(s:str):
    """ Print a warning.

        :param s: The message to print.
    """
    rp(WARNING_PICT + '[yellow]WARNING[/yellow]: ' + s)

def critical(s:str):
    """ Print a critical message.

        :param s: The message to print.

    """
    rp(CRITICAL_PICT + '[red]CRITICAL[/red]: ' + s)

def info(s:str):
    """ Print some extra information.

        :param s: The message to print.
    """
    rp(INFO_PICT + '[cyan]INFO[/cyan]: ' + s)

def debug(s:str):
    """ Print debugging information.

        :param s: The message to print.
    """
    rp(DEBUG_PICT + '[green]DEBUG[/green]; ' + s)


###############################################################################
#   
#   columnize
#   
###############################################################################
def columnize(L:list[str]):
    """ Arrange the list of strings into columns. `rich` handles spacing of its color strings. 
    
        :param L: The list of strings to columnize.
    """
    Console().print(Columns(sorted(L), expand=True, equal=True))


###############################################################################
#   
#   display_doc
#   
###############################################################################
def display_doc(func):
    """
        Display a function or class docstring as Markdown in Jupyter Lab
        safely, avoiding duplicated headers.

        :param func: The function to document.
        :todo: Polish up the output.
    """
    doc = func.__doc__ or ""
    # Split lines and remove any that are blank at the start
    lines = doc.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    cleaned_doc = "\n".join(lines)
    display(Markdown(cleaned_doc))

###############################################################################
#   
#   empty
#   
###############################################################################
@singledispatch
def empty(arg)->bool:
    """Print an error message and depart."""
    error(f': empty : bad argument : {arg} : Argument must be a `list`.')

@empty.register
def _(L:list)->bool:
    """ @return `True` if the `list` is empty, `False` otherwise.
    """
    return len(L) == 0

###############################################################################
#   
#   display_source
#   
###############################################################################
@singledispatch
def display_source(arg)->None:
    """Print an error message and depart."""
    error(f': display_source : bad argument : {arg} : Argument must be str or Path')

@display_source.register
def _(s:str, lang:str='python')->None:
    """ Display the given string as Markdown.

        :param s: String containing source code to display.
        :param lang: Language of the source code.

        :todo: Make sure that `lang` has a valid value.
               If not, just do something generic.
    """
    display(Markdown(f'```{lang}\n{s}'))

@display_source.register
def _(p:Path, lang:str='python')->None:
    """ Open a file and display its contents as source code.

        :param p: Path to the input file.
    """
    display_source(p.read_text(), lang=lang)

@display_source.register
def _(obj:object, lang:str='python')->None:
    """ 
        Display an object's source code as Markdown.

        :param obj: The object.
    """
    display_source(inspect.getsource(obj))

###############################################################################
#   
#   FILE SYSTEM
#   
###############################################################################
# TODO: Left off here with the documentation.
def cwd():
    """Return the current working directory."""
    return Path.cwd()

def pwd():
    """Print `cwd()` and return it."""
    CWD = cwd()
    print(f'{FOLDER_PICT}Current working directory: {CWD}')
    return CWD

def cd(p:str|Path)->Path|None:
    """Change the current working directory."""
    p = Path(p)
    if not p.exists():
        print(f'{WARNING_PICT}WARNING: Directory {str(p)} does not exist!')
        return
    os.chdir(p)
    return p

def hidden(p: Path | str | None) -> bool:
    return any(map(lambda s: s.startswith('.'), p.parts))

def lsd(p: Path | str | None = None, output = True) -> list[Path]:
    """ List the given directory.
        @todo This needs to have a recursive option.
    """
    if not p: p = Path.cwd()
    p = Path(p)
    paths = [path for path in p.glob('*') if not hidden(path)]
    if output:
        pp(list(map(str, paths)))
    return paths

def public(obj)->list:
    """Return the (supposedly) "public" members of the given object."""
    return sorted([s for s in dir(obj) if not s.startswith('_')])

def doxify(text, print_result=True):
    # Just add comment delimiters and asterisks.
    lines = text.split('\n')[1:]
    result = ['/**']
    result.extend([' * ' + s for s in lines])
    result.pop()
    result.append(' */')
    result = '\n'.join(result)
    if print_result: print(result)
    pyperclip.copy(result + NEWLINE)
    print("Docstring copied to clipboard")
    return result

def grepy(
    pattern,
    project_name,
    source_only=True,
    output=True,
) -> list:
    """
        Find `pattern` in the project source directory, presumed to be in `CWD`.
    """
    DEBUG = True
    if output: debug("Running grepy")
    REGEX = grep(pattern, words_only=False)
    FILES = lsd(project_name, output=False)
    TODOS = dict()
    for f in FILES:
        if output: info(f"Scanning {f}")
        lines = list()
        if f.suffix.lstrip(PERIOD) in SRC_FILE_EXTS:
            t = f.read_text()
            m = t | REGEX
        
            LINES = t.split(NEWLINE)
            line_nos = list(m.matches.matching_lines())
            # print(f"`lines` is a {type(m.matches.matching_lines)}.")
            # lines = list(m.matches.matching_lines())
        
            if line_nos:
                n = max(map(lambda i: len(str(i)), line_nos))
                lines = [
                    f"{str(i + 1).rjust(n)}: {LINES[i].lstrip()}"
                    for i in line_nos
                ]

                if source_only:
                    lines = [
                        f"{str(i + 1).rjust(n)}: {LINES[i].lstrip()}"
                        for i in line_nos
                        if not (
                            LINES[i].lstrip().startswith('/') or
                            LINES[i].lstrip().startswith('*') or
                            LINES[i].lstrip().startswith('//')
                        )
                    ]
            
            if lines:
                if output:
                    rp(f"{pattern} found in [yellow]{f.name}[/yellow]:")
                    # lines = [s.lstrip() for s in lines]
                    for s in lines:
                        print(s)
                TODOS[f.name] = lines
                del lines
                
    return TODOS

def now(as_str=False):
    """
        Return the current date and time.
    """
    if as_str: return str(dt.now())
    return dt.now()

@singledispatch
def rdocify(arg, file_doc=False) -> str | None:
    """ Consider this an error. """
    error(f'rdocify : bad argument : {arg} : Argument  must be `str` or `Path`')

@rdocify.register
def _(s: str, file_doc=False) -> str | None:
    s = NEWLINE.join(map(lambda s: CPP_COMMENT + (EXCLAMATION if file_doc else SLASH) + SPACE + s, s.rstrip().split(NEWLINE)[1:]))
    pyperclip.copy(s + NEWLINE)
    return s

@rdocify.register
def _(p:Path, file_doc=False) -> str | None:
    """ Open the file and pass its text to `rdocify(str)`. """
    return rdocify(p.read_text(), file_doc)

def clear():
    """ Clear the outputs of all Jupyter notebook code cells. """
    # print("Running `clear()`...")
    for path in Path("lab").glob("*.ipynb"):
        notebook = nbformat.read(path, as_version=4)
        # print(f"Clearing {path}")

        for cell in notebook.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None

        nbformat.write(notebook, path)
        print(f"{CHECK_PICT} Jupyter output cleared.")
        return 0
    
def banner(text: str, style="rust") -> str | None:
    """ Convert `s` to a source code banner. """
    # `style` must be "py" or "rust"
    if not style in COMMENT_STYLES:
        error("Unknown style")
        return
    if style == "rust":
        left = ASTERISK + SPACE * 3
        top = SLASH + COMMENT_BORDER + NEWLINE + ASTERISK + NEWLINE
        bottom = ASTERISK + NEWLINE + BOTTOM_BORDER + NEWLINE
    elif style == "py":
        left = HASH_MARK + SPACE * 3
        top = PY_COMMENT_BORDER + NEWLINE + left + NEWLINE
        bottom = left + NEWLINE + PY_COMMENT_BORDER + NEWLINE
    value = top + NEWLINE.join([
        left + s for s in text.strip().split(NEWLINE)
    ]) + NEWLINE + bottom
    pyperclip.copy(value)
    return value