# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_clean.ipynb.

# %% auto 0
__all__ = ['CONSOLE', 'CLEAN_TABLE', 'colab_json', 'cell_metadata_keep', 'nb_metadata_keep', 'rm_execution_count',
           'clean_output_data_vnd', 'clean_cell_output', 'clean_cell', 'clean_nb', 'clean_one', 'clean_all',
           'clean_nbs']

# %% ../nbs/04_clean.ipynb 3
import io, json, os
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import track
from fastcore.script import call_parse, Param, store_true
from execnb.nbio import read_nb

from .utils import print_output, is_nb, find_nbs

# %% ../nbs/04_clean.ipynb 5
def _create_table():
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Notebook Path", style="dim")
    table.add_column("Status")
    return table

# %% ../nbs/04_clean.ipynb 6
CONSOLE = Console()

# %% ../nbs/04_clean.ipynb 7
CLEAN_TABLE = _create_table()

# %% ../nbs/04_clean.ipynb 9
def rm_execution_count(o):
    "Remove execution count in `o`"
    if "execution_count" in o:
        o["execution_count"] = None

# %% ../nbs/04_clean.ipynb 10
colab_json = "application/vnd.google.colaboratory.intrinsic+json"

# %% ../nbs/04_clean.ipynb 11
def clean_output_data_vnd(o):
    "Remove `application/vnd.google.colaboratory.intrinsic+json` in data entries"
    if "data" in o:
        data = o["data"]
        if colab_json in data:
            new_data = {k: v for k, v in data.items() if k != colab_json}
            o["data"] = new_data

# %% ../nbs/04_clean.ipynb 12
def clean_cell_output(cell):
    "Remove execution count in `cell`"
    if "outputs" in cell:
        for o in cell["outputs"]:
            rm_execution_count(o)
            clean_output_data_vnd(o)
            o.get("metadata", o).pop("tags", None)

# %% ../nbs/04_clean.ipynb 13
cell_metadata_keep = ["hide_input"]

# %% ../nbs/04_clean.ipynb 14
nb_metadata_keep = ["kernelspec", "accelerator", "colab"]

# %% ../nbs/04_clean.ipynb 15
def clean_cell(cell, clear_all=False):
    "Clean `cell` by removing superfluous metadata or everything except the input if `clear_all`"
    rm_execution_count(cell)
    if "outputs" in cell:
        if clear_all:
            cell["outputs"] = []
        else:
            clean_cell_output(cell)
    if cell["source"] == [""]:
        cell["source"] = []
    cell["metadata"] = {} if clear_all else {k: v for k, v in cell["metadata"].items() if k in cell_metadata_keep}

# %% ../nbs/04_clean.ipynb 16
def clean_nb(nb, clear_all=False):
    "Clean `nb` from superfluous metadata, passing `clear_all` to `clean_cell`"
    for c in nb["cells"]:
        clean_cell(c, clear_all=clear_all)
    nb["metadata"] = {k: v for k, v in nb["metadata"].items() if k in nb_metadata_keep}

# %% ../nbs/04_clean.ipynb 18
def clean_one(fname: Path, clear_outs: bool = False, disp: bool = False):
    """Clean notebook metadata:
    - `clear_all` removes also outputs
    - `disp` prints to stdout
    """
    if not is_nb(fname):
        print(f"This {fname}: is not a notebook my friend")
        return
    notebook = json.load(open(str(fname), "r", encoding="utf-8"))
    clean_nb(notebook, clear_all=clear_outs)
    if disp:
        print_output(notebook)
    else:
        x = json.dumps(notebook, sort_keys=True, indent=1, ensure_ascii=False)
        with io.open(fname, "w", encoding="utf-8") as f:
            f.write(x)
            f.write("\n")

# %% ../nbs/04_clean.ipynb 20
def clean_all(path: Path, clear_outs=True, disp=False):
    "Apply clean to all nbs inside path recursvely"

    for nb in track(find_nbs(path), "Cleaning nbs..."):
        try:
            clean_one(nb, clear_outs, disp)
            CLEAN_TABLE.add_row(str(nb), "[green]Ok[/green]:heavy_check_mark:")
        except:
            CLEAN_TABLE.add_row(str(nb), "[red]Failed[/red]")

# %% ../nbs/04_clean.ipynb 22
@call_parse
def clean_nbs(
    path: Param("A path to nb files", Path, nargs="?", opt=False) = os.getcwd(),
    clear_outs: Param("Remove cell outputs", store_true) = False,
    verbose: Param("Rnun on verbose mdoe", store_true) = False,
):
    "Clean notebooks on `path` from useless metadata"
    path = Path(path)
    clean_all(path, clear_outs, disp=verbose)
    CONSOLE.print(CLEAN_TABLE)
