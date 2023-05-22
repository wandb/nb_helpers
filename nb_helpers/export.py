# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_export.ipynb.

# %% auto 0
__all__ = ['default_line_filter', 'filter_out_lines', 'export_cell', 'colab_url', 'export']

# %% ../nbs/06_export.ipynb 3
import os
from pathlib import Path
from rich.markdown import Markdown
from fastcore.script import call_parse, Param, store_true

from .colab import has_colab_badge, get_colab_url
from .utils import find_nbs, read_nb, is_nb

# %% ../nbs/06_export.ipynb 8
def _export_code_cell(source):
    "Wrap code around python"
    return f"\n```python\n{source}\n```\n\n"

def default_line_filter(line):
    if "colab.research" in line:
        return False
    elif "@wandbcode" in line:
        return False
    else: 
        return True

def filter_out_lines(source, f=default_line_filter):
    "Filter lines from source with filter f"
    lines = source.split("\n")
    return "\n".join(filter(f, lines))

def _export_md_cell(source):
    source = filter_out_lines(source)
    return f"{source} \n"

# %% ../nbs/06_export.ipynb 9
def export_cell(cell, debug=False):
    "Export cell source to string"
    source = cell["source"]
    if debug:
        print(source)
    if cell["cell_type"] == "markdown":
        return _export_md_cell(source)
        
    elif cell["cell_type"] == "code":
        return  _export_code_cell(source)
    else:
        return ""

# %% ../nbs/06_export.ipynb 12
def colab_url(file):
    "Create a fresh colab URL from file, must be on github repo"
    url = get_colab_url(file, branch="master")
    return f'\n[![](https://colab.research.google.com/assets/colab-badge.svg)]({url})\n\n'

# %% ../nbs/06_export.ipynb 17
@call_parse
def export(
    path: Param("A path to nb files", Path, nargs="?", opt=False) = os.getcwd(),
    verbose: Param("Print errors along the way", store_true) = False,
    outfile: Param("An output file to save") = None,
):
    if is_nb(path):
        nb = read_nb(path)
    else:
        raise Error(f"This {path} is not a notebook!")
    
    if outfile is None:
        outfile = path.with_suffix(".md")
        print(f"Exporting notebook {path} -> {outfile}")
    
    cells = notebook["cells"]
    export_cells = [export_cell(c) for c in cells]
    
    with open(outfile, "w") as f:
        f.writelines(export_cells)