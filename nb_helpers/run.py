import time
from pathlib import Path
from types import SimpleNamespace
from typing import Union, List
from tempfile import TemporaryDirectory
from fastcore.basics import listify

import nbformat
from fastcore.script import *
from rich import print as pprint
from rich.console import Console
from rich.table import Table
from rich.progress import track

from nb_helpers.utils import find_nbs, git_origin_repo, is_nb, search_string_in_nb, read_nb
from nb_helpers.nbdev_test import NoExportPreprocessor, get_all_flags

FEATURES = ["Path", "os", "chain", "Union", "sleep"]
## ["WandbCallback", "WandbLogger", "Table", "Artifact", "sweep"]

__all__ = ["run_one", "test_nbs"]


def _create_table(xtra_col=None) -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Notebook Path", style="dim")
    table.add_column("Status")
    table.add_column("Run Time")
    table.add_column("Colab", style="blue u")
    if xtra_col is not None:
        table.add_column(xtra_col)
    return table


STATUS = SimpleNamespace(
    ok="[green]Ok[/green]:heavy_check_mark:", fail="[red]Fail[/red]", skip="[green]Skipped[/green]:heavy_check_mark:"
)


def _format_row(fname: Path, status: str, time: str, github_repo: str, xtra_col=None) -> tuple:
    "Format one row for a rich.Table"

    formatted_status = getattr(STATUS, status.lower())
    link = f"[link=https://colab.research.google.com/{github_repo}/{str(fname)}]open[link]"

    row = (str(fname), formatted_status, f"{int(time)} s", link)
    if len(listify(xtra_col)) > 0:
        row += (str(xtra_col),)
    return row


def skip_nb(notebook, flags=None, filters=None):
    "check for notebook flags: all_skip, all_slow and filters: tensorflow, pytorch, ..."
    skip = False
    for f in get_all_flags(notebook["cells"]):
        if f not in listify(flags):
            skip = True
    if not search_string_in_nb(notebook, filters):
        skip = True
    return skip


def _exec_nb(notebook, flags=None, timeout=600):
    "run notebook"
    processor = NoExportPreprocessor(flags, timeout=timeout, kernel_name="python3")
    processed_nb = nbformat.from_dict(notebook)
    with TemporaryDirectory() as temp_dir:
        processor.preprocess(processed_nb, {"metadata": {"path": temp_dir}})
    return True

def run_one(
    fname: Union[Path, str],
    verbose: bool = False,
    timeout: int = 600,
    flags: List[str] = None,
    lib_name: str = None,
    no_run: bool = False,
):
    "Run nb `fname` and timeit, recover exception"
    github_repo = git_origin_repo()
    start = time.time()
    did_run, skip, error = False, False, None
    flags = listify(flags)
    try:
        # read notebook as dict
        notebook = read_nb(fname)

        #check if notebooks has to be runned
        skip = skip_nb(notebook, flags, lib_name)
        if skip or no_run:
            return _format_row(fname, "skip", time.time() - start, github_repo), None
        else:
            did_run = _exec_nb(notebook, flags, timeout)
    except Exception as e:
        if verbose:
            print(f"\nError in {fname}:\n{e}")
            error = e
        error = e
    return (
        _format_row(fname, "ok" if did_run else "fail", time.time() - start, github_repo),
        error,
    )


@call_parse
def run_nbs(
    path: Param("A path to nb files", str) = ".",
    verbose: Param("Print errors along the way", store_true) = False,
    flags: Param("Space separated list of flags", str) = None,
    timeout: Param("Max runtime for each notebook, in seconds", int) = 600,
    lib_name: Param("Python lib names to filter, eg: tensorflow", str) = None,
    no_run: Param("Do not run any notebook", store_true) = False, 
):
    console = Console(width=180)
    print(f"CONSOLE.is_terminal(): {console.is_terminal}")
    table = _create_table()
    path = Path(path)
    if is_nb(path):
        files = [path]
    else:
        files = find_nbs(path)
    pprint(f"Testing {len(files)} notebooks")
    failed_nbs = {}
    for nb in track(files, description="Running nbs..."):
        row, e = run_one(nb, verbose=verbose, timeout=timeout, flags=flags, lib_name=lib_name, no_run=no_run)
        pprint(f" > {row[0]:80} | {row[1]:40} | {row[2]:5} | {row[3]}")
        table.add_row(*row)
        time.sleep(0.1)
        if e is not None:
            failed_nbs[str(nb)] = e
    console.print(table)
    console.print("END!")

    return failed_nbs

