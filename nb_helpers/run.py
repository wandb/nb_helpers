import time
from pathlib import Path
from typing import Union, List
from tempfile import TemporaryDirectory
from fastcore.basics import listify

import nbformat
from nbformat import NotebookNode
from fastcore.xtras import run
from fastcore.script import *
from rich import print as pprint
from rich.console import Console
from rich.table import Table
from rich.progress import track

from nb_helpers.utils import find_nbs, git_origin_repo, is_nb, search_string_in_code
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


def _format_row(fname: Path, status: str, time: str, github_repo: str, xtra_col=None) -> tuple:
    "Format one row for a rich.Table"

    if status.lower() == "ok":
        status = "[green]Ok[/green]:heavy_check_mark:"
    elif status.lower() == "skip":
        status = "[green]Skipped[/green]:heavy_check_mark:"
    else:
        status = "[red]Fail[/red]"

    link = f"[link=https://colab.research.google.com/{github_repo}/{str(fname)}]open[link]"

    row = (str(fname), status, f"{int(time)} s", link)
    if len(listify(xtra_col)) > 0:
        row += (str(xtra_col),)
    return row


def read_nb(fname: Union[Path, str]) -> NotebookNode:
    "Read the notebook in `fname`."
    with open(Path(fname), "r", encoding="utf8") as f:
        return nbformat.reads(f.read(), as_version=4)


def run_one(
    fname: Union[Path, str],
    verbose: bool = False,
    timeout: int = 600,
    flags: List[str] = None,
    lib_name: str = None,
    features: List[str] = None,
):
    "Run nb `fname` and timeit, recover exception"
    github_repo = git_origin_repo()
    start = time.time()
    did_run, skip, error = False, False, None
    if flags is None:
        flags = []
    try:
        # read notebook as dict
        notebook = read_nb(fname)

        # check for notebook flags: all_skip, all_slow
        for f in get_all_flags(notebook["cells"]):
            if f not in flags:
                skip = True
                break

        # search code for specific strings in code: io, Path, list, etc...
        features_used = []
        for feat in listify(features):
            if search_string_in_code(notebook, feat):
                features_used.append(feat)

        # check for specific libs: tensorflow, pytorch, sklearn, xgboost...
        if not search_string_in_code(notebook, lib_name):
            skip = True
        if skip:
            return _format_row(fname, "skip", time.time() - start, github_repo, xtra_col=features_used), None
        else:
            processor = NoExportPreprocessor(flags, timeout=timeout, kernel_name="python3")
            pnb = nbformat.from_dict(notebook)
            with TemporaryDirectory() as temp_dir:
                processor.preprocess(pnb, {"metadata": {"path": temp_dir}})
            did_run = True
    except Exception as e:
        if verbose:
            print(f"\nError in {fname}:\n{e}")
            error = e
        error = e
    return (
        _format_row(fname, "ok" if did_run else "fail", time.time() - start, github_repo, xtra_col=features_used),
        error,
    )


@call_parse
def test_nbs(
    path: Param("A path to nb files", str) = ".",
    verbose: Param("Print errors along the way", store_true) = False,
    flags: Param("Space separated list of flags", str) = None,
    timeout: Param("Max runtime for each notebook, in seconds", int) = 600,
    lib_name: Param("Python lib names to filter, eg: tensorflow", str) = None,
    features: Param("Expresion used inside the code cells, eg: itertools.chain, Path,. Pass as comma separated", str) = None, 
):
    console = Console(width=180)
    print(f"CONSOLE.is_terminal(): {console.is_terminal}")
    if features is not None:
        features = features.split(",")
    table = _create_table("Features" if features else None)
    path = Path(path)
    if is_nb(path):
        files = [path]
    else:
        files = find_nbs(path)
    pprint(f"Testing {len(files)} notebooks")
    failed_nbs = {}
    for nb in track(files, description="Running nbs..."):
        row, e = run_one(nb, verbose=verbose, timeout=timeout, flags=flags, lib_name=lib_name, features=features)
        pprint(f" > {row[0]:80} | {row[1]:40} | {row[2]:5} | {row[3]}")
        table.add_row(*row)
        time.sleep(0.1)
        if e is not None:
            failed_nbs[str(nb)] = e
    console.print(table)
    console.print("END!")

    return failed_nbs
