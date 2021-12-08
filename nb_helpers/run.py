import time
from pathlib import Path
from tempfile import TemporaryDirectory

from fastcore.xtras import run
from fastcore.script import *
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import track
import nbformat

from nb_helpers.utils import find_nbs, git_origin_repo, is_nb, uses_lib, is_colab
from nb_helpers.nbdev_test import NoExportPreprocessor, get_all_flags


def _create_table():
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Notebook Path", style="dim")
    table.add_column("Status")
    table.add_column("Run Time")
    table.add_column("Colab", style="blue u")
    return table


CONSOLE = Console(width=180)
print(f"CONSOLE.is_terminal(): {CONSOLE.is_terminal}")
RUN_TABLE = _create_table()
GITHUB_REPO = git_origin_repo()


def _format_row(fname, status, time):
    "Format one row for a rich.Table"

    if status.lower() == "ok":
        status = "[green]Ok[/green]:heavy_check_mark:"
    elif status.lower() == "skip":
        status = "[green]Skipped[/green]:heavy_check_mark:"
    else:
        status = "[red]Fail[/red]"

    link = f"[link=https://colab.research.google.com/{GITHUB_REPO}/{fname}]open in colab[link]"

    row = (str(fname), status, f"{int(time)} s", link)
    return row


def read_nb(fname):
    "Read the notebook in `fname`."
    with open(Path(fname), "r", encoding="utf8") as f:
        return nbformat.reads(f.read(), as_version=4)


def run_one(fname, verbose=False, timeout=600, flags=None, lib_name=None):
    "Run nb `fname` and timeit, recover exception"
    start = time.time()
    did_run, skip = False, False
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

        # check for specific libs: tensorflow, pytorch, sklearn, xgboost...
        if not uses_lib(notebook, lib_name):
            skip = True
        if skip:
            return _format_row(fname, "skip", time.time() - start)
        else:
            processor = NoExportPreprocessor(flags, timeout=timeout, kernel_name="python3")
            pnb = nbformat.from_dict(notebook)
            with TemporaryDirectory() as temp_dir:
                processor.preprocess(pnb, {"metadata": {"path": temp_dir}})
            did_run = True
    except Exception as e:
        if verbose:
            print(f"\nError in executing {fname}\n{e}\n")
        else:
            pass
    return _format_row(fname, "ok" if did_run else "fail", time.time() - start)


@call_parse
def test_nbs(
    path: Param("A path to nb files", str) = ".",
    verbose: Param("Print errors along the way", store_true) = False,
    flags: Param("Space separated list of flags", str) = None,
    timeout: Param("Max runtime for each notebook, in seconds", int) = 600,
    lib_name: Param("Python lib names to filter, eg: tensorflow", str) = None,
):
    path = Path(path)
    if is_nb(path):
        files = [path]
    else:
        files = find_nbs(path)
    results = []
    for nb in track(files, description="Running nbs..."):
        row = run_one(nb, verbose=verbose, timeout=timeout, flags=flags, lib_name=lib_name)
        print(f' > {row[0]:80} | {row[1]:40} | {row[2]:5}')
        RUN_TABLE.add_row(*row)
        time.sleep(0.5)
    CONSOLE.print(RUN_TABLE)
    CONSOLE.print("END!")
