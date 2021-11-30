import io, json, sys
from pathlib import Path

from rich import print
from rich.console import Console
from rich.table import Table
from fastcore.script import *
from fastprogress import progress_bar

from nbdev.clean import clean_nb
from nb_helpers.utils import print_output, is_nb, find_nbs


def _create_table():
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Notebook Path", style="dim")
    table.add_column("Status")
    return table


CONSOLE = Console()
CLEAN_TABLE = _create_table()


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


def clean_all(path: Path, clear_outs=True, disp=False):
    "Apply clean to all nbs inside path recursvely"

    for nb in progress_bar(find_nbs(path), leave=False):
        try:
            clean_one(nb, clear_outs, disp)
            CLEAN_TABLE.add_row(str(nb), "[green]Ok[/green]:heavy_check_mark:")
        except:
            CLEAN_TABLE.add_row(str(nb), "[red]Failed[/red]")


@call_parse
def clean_nbs(
    path: Param("The path to notebooks", str) = ".",
    clear_outs: Param("Remove cell outputs", store_true) = False,
    verbose: Param("Rnun on verbose mdoe", store_true) = False,
):
    "Clean notebooks on `path` from useless metadata"
    path = Path(path)
    clean_all(path, clear_outs, disp=verbose)
    CONSOLE.print(CLEAN_TABLE)
