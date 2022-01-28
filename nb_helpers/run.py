import time
from pathlib import Path
from types import SimpleNamespace
from typing import Union, List
from tempfile import TemporaryDirectory
from fastcore.basics import listify

import nbformat
from fastcore.script import *
from rich import print as pprint
from rich.progress import track

from nb_helpers.utils import find_nbs, search_string_in_nb, read_nb, RichLogger
from nb_helpers.colab import get_colab_url
from nb_helpers.nbdev_test import NoExportPreprocessor, get_all_flags

FEATURES = ["Path", "os", "chain", "Union", "sleep"]
## ["WandbCallback", "WandbLogger", "Table", "Artifact", "sweep"]

__all__ = ["run_one", "run_nbs"]


STATUS = SimpleNamespace(
    ok="[green]Ok[/green]:heavy_check_mark:", fail="[red]Fail[/red]", skip="[green]Skipped[/green]:heavy_check_mark:"
)


def _format_row(fname: Path, status: str, time: str, xtra_col=None, fname_only: bool = True) -> tuple:
    "Format one row for a rich.Table"

    formatted_status = getattr(STATUS, status.lower())
    fname = fname.name if fname_only else fname
    row = (str(fname), formatted_status, f"{int(time)}s")
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


def exec_nb(notebook, flags=None, timeout=600, use_temp_dir=True, pip_install=True):
    "run notebook, possible skiping cells with flags"
    processor = NoExportPreprocessor(flags, pip_install=pip_install, timeout=timeout, kernel_name="python3")
    processed_nb = nbformat.from_dict(notebook)
    with TemporaryDirectory() as temp_dir:
        resources = {"metadata": {"path": temp_dir}} if use_temp_dir else None
        processor.preprocess(processed_nb, resources)
    return True


def run_one(
    fname: Union[Path, str],
    verbose: bool = False,
    timeout: int = 600,
    flags: List[str] = None,
    lib_name: str = None,
    no_run: bool = False,
    pip_install=True,
):
    "Run nb `fname` and timeit, recover exception"
    start = time.time()
    did_run, skip, error = False, False, None
    flags = listify(flags)
    try:
        # read notebook as dict
        notebook = read_nb(fname)

        # check if notebooks has to be runned
        skip = skip_nb(notebook, flags, lib_name)

        if skip or no_run:
            return _format_row(fname, "skip", time.time() - start), None
        else:
            did_run = exec_nb(notebook, flags, timeout, pip_install=pip_install)
    except Exception as e:
        if verbose:
            print(f"\nError in {fname}:\n{e}")
            error = e
        error = e
    return (
        _format_row(fname, "ok" if did_run else "fail", time.time() - start),
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
    post_issue: Param("Post the failure in github", store_true) = False,
    no_install: Param("Do not install anything with pip", store_false) = False,
):
    logger = RichLogger(columns=["fname", "status", "t[s]"])
    path = Path(path)
    files = find_nbs(path)

    failed_nbs = {}
    for nb_path in track(files, description="Running nbs..."):
        (fname, run_status, runtime), e = run_one(
            nb_path,
            verbose=verbose,
            timeout=timeout,
            flags=flags,
            lib_name=lib_name,
            no_run=no_run,
            pip_install=no_install,
        )
        pprint(f" > {fname:80} | {run_status:40} | {runtime:5} ")
        logger.writerow([fname, run_status, runtime], colab_link=get_colab_url(nb_path))
        time.sleep(0.1)
        if e is not None:
            failed_nbs[str(nb_path)] = e

    logger.to_table()
    logger.to_md("run.md")
    return failed_nbs
