###############################################################################
#   
#   NOTEBOOK TOOLS
#   
###############################################################################
from datetime import datetime as dt
from functools import partial, singledispatch
import inspect
import os
from pathlib import Path
from pprint import pprint as pp
import subprocess
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
#   DOCSTRING
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
#   LIST TOOLS
#   
###############################################################################

# ══════════════════════════════════ empty ══════════════════════════════════
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
#   DATES & TIMES
#   
###############################################################################

# ═══════════════════════════════════ now ═══════════════════════════════════
def now(as_str=False):
    """
        Return the current date and time.
    """
    if as_str: return str(dt.now())
    return dt.now()

###############################################################################
#   
#   OUTPUT
#   
###############################################################################

# ══════════════════════════════════ error ══════════════════════════════════
def error(s:str):
    """ Print an error message.

        :param s: The message to print.
    """
    rp(ERROR_PICT + '[red]ERROR[/red]: ' + s)

# ══════════════════════════════════ warn ══════════════════════════════════
def warn(s:str):
    """ Print a warning.

        :param s: The message to print.
    """
    rp(WARNING_PICT + '[yellow]WARNING[/yellow]: ' + s)

# ════════════════════════════════ critical ════════════════════════════════
def critical(s:str):
    """ Print a critical message.

        :param s: The message to print.

    """
    rp(CRITICAL_PICT + '[red]CRITICAL[/red]: ' + s)

# ══════════════════════════════════ info ══════════════════════════════════
def info(s:str):
    """ Print some extra information.

        :param s: The message to print.
    """
    rp(INFO_PICT + '[cyan]INFO[/cyan]: ' + s)

# ══════════════════════════════════ debug ══════════════════════════════════
def debug(s:str):
    """ Print debugging information.

        :param s: The message to print.
    """
    rp(DEBUG_PICT + '[green]DEBUG[/green]; ' + s)


# ════════════════════════════════ columnize ════════════════════════════════
def columnize(L:list[str]):
    """ Arrange the list of strings into columns. `rich` handles spacing of its color strings. 
    
        :param L: The list of strings to columnize.
    """
    Console().print(Columns(sorted(L), expand=True, equal=True))


###############################################################################
#   
#   FILE SYSTEM
#   
###############################################################################

# ═══════════════════════════════════ cwd ═══════════════════════════════════
def cwd()-> Path:
    """ # Return
          `Path` to the current working directory.
    """
    return Path.cwd()

# ═══════════════════════════════════ pwd ═══════════════════════════════════
def pwd():
    """Print `cwd()` and return it."""
    CWD = cwd()
    print(f'{FOLDER_PICT}Current working directory: {CWD}')
    return CWD

# ═══════════════════════════════════ cd ═══════════════════════════════════
def cd(p:str|Path)->Path|None:
    """Change the current working directory."""
    p = Path(p)
    if not p.exists():
        print(f'{WARNING_PICT}WARNING: Directory {str(p)} does not exist!')
        return
    os.chdir(p)
    return p

# ═════════════════════════════════ hidden ═════════════════════════════════
def hidden(p: Path | str | None) -> bool:
    """ # Return

        `True` if any part of the `Path` is hidden (`.startswith('.')`).

        🚧 _TODO_: Really should include files that end with `'~'`, `'#'`, etc. 
    """
    return any(map(lambda s: s.startswith('.'), p.parts))

# ═══════════════════════════════════ lsd ═══════════════════════════════════
def lsd(p: Path | str | None = None, output = True) -> list[Path]:
    """ List the given directory.

        # Parameters

            * `p`: `Path` to the directory, a `str` representing that
                   path, or `None`, in which case `cwd` is assumed.
            * `output`: Whether to print the resulting list. `True` by default.
            
        # Return

        A `list` of the files within `p`.
        
        🚧 _TODO_:  This needs to have a recursive option.
        🚧 _TODO_:  Fancy colored output like `bash` displays.

    """
    if not p: p = Path.cwd()
    p = Path(p)
    paths = [path for path in p.glob('*') if not hidden(path)]
    if output:
        pp(list(map(str, paths)))
    return paths

###############################################################################
#   
#   OBJECT TOOLS
#   
###############################################################################

# ═════════════════════════════════ public ═════════════════════════════════
def public(obj)->list:
    """Return the (supposedly) "public" members of the given object."""
    return sorted([s for s in dir(obj) if not s.startswith('_')])

###############################################################################
#   
#   TEXT TOOLS
#   
###############################################################################

# ══════════════════════════════════ grepy ══════════════════════════════════
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


###############################################################################
#   
#   DOCUMENTATION
#   
###############################################################################

# ═══════════════════════════════ display_doc ═══════════════════════════════
def display_doc(func):
    """
        Display a function or class docstring as Markdown in Jupyter Lab
        safely, avoiding duplicated headers.

        :param func: The function to document.
        🚧 _TODO_: Polish up the output. Right now it's not displayed as Markdown.
               The problem is indentation of the docstring.
    """
    doc = func.__doc__.strip() or ""
    # Split lines and remove any that are blank at the start
    lines = doc.splitlines()
    print(f"Number of lines: {len(lines)}")
    print(f"First line: {lines[1]}")
    print(f"Length of `lines[0]`: {len(lines[1])}")
    leading_spaces = 0
    i = 0
    j = 0
    for i in range(len(lines[0])):
        if lines[0][i] != SPACE:
            break
        leading_spaces += 1
        
    print(i)
    print(lines[0][0])
    lines = [ line[leading_spaces:] for line in lines ]
    cleaned_doc = "\n".join(lines)
    display(Markdown(cleaned_doc))

# ═════════════════════════════ display_source ═════════════════════════════
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
# ═════════════════════════════════ rdocify ═════════════════════════════════
@singledispatch
def rdocify(arg, file_doc=False) -> str | None:
    """ Consider this an error. """
    error(f'rdocify : bad argument : {arg} : Argument  must be `str` or `Path`')

@rdocify.register
def _(s: str, file_doc=False) -> str | None:
    s = NEWLINE.join(map(lambda s: CPP_COMMENT + (EXCLAMATION if file_doc else SLASH)
                                   + SPACE + s, s.rstrip().split(NEWLINE)[1:]))
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
    
# ══════════════════════════════════ banner ══════════════════════════════════
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

syscmd = partial(subprocess.run, text=True, capture_output=True, shell=True)

# ══════════════════════════════ function_header ══════════════════════════════
def function_header(s: str, style="rust", bar_width=16) -> str:
    """
        Decorate a string with a bar heading like the one above.

        # Parameters

        ## Arguments

            * `s`: The string to decorate.

        ## Keyword Arguments
        
            * `style`: The comment style. Can (must) be `'py'` or `'rust'`.
                       `'rust'` by default.
            * `bar_width`: _Deprecated_
    """
    LEFT = HASH_MARK if style=="py" else CPP_COMMENT
    BAR_WIDTH = int((SOURCE_TEXT_WIDTH - len(s) - len(LEFT) - 3) / 2)
    BAR = BOX_DRAWING_DOUBLE_HORIZONTAL * BAR_WIDTH
    value = LEFT + SPACE + BAR + SPACE + s.strip() + SPACE + BAR + NEWLINE
    pyperclip.copy(value)
    return value
    
# ══════════════════════════════ block_comment ══════════════════════════════
def block_comment(s: str, indents=(0,4), style='rust') -> str:
    """ Encase `s` in a block comment. 

        # Parameters

            * `s``
              : The comment string, presumably multiple lines.
            * `indents`
              : A tuple. `[0]` is the number of tabs.
                         `[1]` is the number of spaces in each tab.

        # Return
        
            The parameter string as a block comment in the requested style.

        # TODO

            * Wrap `s` to a width that will fit within `SOURCE_TEXT_WIDTH`.
              That's currently on the user to ensure, if it gets done at all.
    """
    text_lines = s.strip().split(NEWLINE)
    LEFT = HASH_MARK if style == 'py' else CPP_COMMENT
    output_lines = [ LEFT + SPACE + line for line in text_lines ]
    return NEWLINE.join(output_lines)

# ══════════════════════════════ typing_guide ══════════════════════════════
def typing_guide():
    print(SPACE * 71 + WARNING_PICT + "==> " + CRITICAL_PICT)

