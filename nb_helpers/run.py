import time
from pathlib import Path

from fastcore.script import *
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import track
import nbformat

from nb_helpers.utils import find_nbs
from nb_helpers.nbdev_test import NoExportPreprocessor, get_all_flags


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


def run_one(fname, verbose=False, timeout=600, flags=None):
    "Run nb `fname` and timeit, recover exception"
    start = time.time()
    did_run = False
    if flags is None:
        flags = []
    try:
        notebook = read_nb(fname)
        for f in get_all_flags(notebook["cells"]):
            if f not in flags:
                RUN_TABLE.add_row(
                    str(fname),
                    "[green]Skipped[/green]:heavy_check_mark:",
                    f"{int(time.time() - start)} s",
                    f"[blue u link=https://colab.research.google.com/{GITHUB_REPO}/{fname}]open in colab[/blue u link]",
                )
                return did_run, time.time() - start
        processor = NoExportPreprocessor(flags, timeout=timeout, kernel_name="python3")
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
        f"[blue u link=https://colab.research.google.com/{GITHUB_REPO}/{fname}]open in colab[/blue u link]",
    )
    # CONSOLE.print(f'open in colab', style=f'link "https://colab.research.google.com/{GITHUB_REPO}/{fname}"')
    return did_run, time.time() - start


@call_parse
def test_nbs(
    path: Param("A notebook name or glob to convert", str) = ".",
    verbose: Param("Print errors along the way", store_true) = False,
    flags: Param("Space separated list of flags", str) = None,
    timeout: Param("Max runtime for each notebook, in seconds", int) = 600,
    timing: Param("Timing each notebook to see the ones are slow", store_true) = False,
):
    files = find_nbs(Path(path))
    results = []
    for nb in track(files, description="Running nbs..."):
        print(f"  > {nb}")
        results.append(run_one(nb, verbose=verbose, timeout=timeout, flags=flags))
        time.sleep(0.5)
    _, times = [r[0] for r in results], [r[1] for r in results]
    CONSOLE.print(RUN_TABLE)
    if timing:
        for i, t in sorted(enumerate(times), key=lambda o: o[1], reverse=True):
            print(f"Notebook {files[i].name} took {int(t)} seconds")
