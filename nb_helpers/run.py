from ast import Param
import glob
import time
from pathlib import Path

from fastcore.script import *
from rich import print
from rich.console import Console
from rich.table import Table
import nbformat
from fastcore.basics import num_cpus
from nbconvert.preprocessors import ExecutePreprocessor

from nb_helpers.utils import find_nbs


def _create_table():
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Notebook Path", style="dim")
    table.add_column("Status")
    table.add_column("Run Time")
    table.add_column("Colab", style="blue u")
    return table


CONSOLE = Console()
RUN_TABLE = _create_table()

GITHUB_REPO = "github/wandb/examples/blob/master"


def read_nb(fname):
    "Read the notebook in `fname`."
    with open(Path(fname), "r", encoding="utf8") as f:
        return nbformat.reads(f.read(), as_version=4)


def run_one(fname, verbose=False):
    "Run nb `fname` and timeit, recover exception"
    print(f"testing {fname}")
    start = time.time()
    did_run = False
    try:
        notebook = read_nb(fname)
        processor = ExecutePreprocessor(timeout=600, kernel_name="python3")
        pnb = nbformat.from_dict(notebook)
        processor.preprocess(pnb)
        did_run = True
    except Exception as e:
        if verbose:
            print(f"\nError in executing {fname}\n{e}\n")
        else:
            pass

    RUN_TABLE.add_row(
        str(fname),
        "[green]Ok[/green]:heavy_check_mark:" if did_run else "[red]Fail[/red]",
        f"{int(time.time() - start)} s",
        f"[u blue]https://colab.research.google.com/{GITHUB_REPO}/{fname}[\blue u]",
    )
    # CONSOLE.print(f'open in colab', style=f'link "https://colab.research.google.com/{GITHUB_REPO}/{fname}"')
    return did_run, time.time() - start


@call_parse
def test_nbs(
    path: Param("A notebook name or glob to convert", str) = ".",
    verbose: Param("Print errors along the way", store_true) = False,
    timing: Param("Timing each notebook to see the ones are slow", store_true) = False,
):
    files = find_nbs(Path(path))
    results = []
    for nb in files:
        results.append(run_one(nb, verbose=verbose))
        time.sleep(0.5)
    _, times = [r[0] for r in results], [r[1] for r in results]
    CONSOLE.print(RUN_TABLE)
    if timing:
        for i, t in sorted(enumerate(times), key=lambda o: o[1], reverse=True):
            print(f"Notebook {files[i].name} took {int(t)} seconds")
