import time
from pathlib import Path
from logging import warning
from types import SimpleNamespace
from typing import Union, List
from tempfile import TemporaryDirectory
from fastcore.basics import listify

import nbformat
from fastcore.script import *
from rich import print as pprint
from rich.progress import track

from execnb.nbio import read_nb as read_nb
from execnb.shell import CaptureShell

from nb_helpers.utils import find_nbs, git_main_name, search_string_in_nb, RichLogger
from nb_helpers.colab import get_colab_url



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


def skip_nb(notebook, filters=None):
    "check for notebook filters: tensorflow, pytorch, ..."
    skip = False
    if not search_string_in_nb(notebook, filters):
        skip = True
    return skip


def exec_nb(fname, do_print=False, pip_install=True):
    "Execute tests in notebook in `fn` "
    nb = read_nb(fname)
    def _no_eval(cell):
        if "pip" in cell.source and not pip_install:
            return True
        if cell.cell_type != 'code': 
            return True
        else:
            return False
    
    start = time.time()
    k = CaptureShell(fname)
    if do_print: print(f'Starting {fname}')
    k.run_all(nb, exc_stop=True, preproc=_no_eval)
    res = True
    if do_print: print(f'- Completed {fname}')
    return res,time.time()-start

# def exec_nb(notebook, timeout=600, use_temp_dir=True, pip_install=True):
#     "run notebook, possible skiping cells"
#     processor = NoExportPreprocessor(pip_install=pip_install, timeout=timeout, kernel_name="python3")
#     processed_nb = nbformat.from_dict(notebook)
#     with TemporaryDirectory() as temp_dir:
#         resources = {"metadata": {"path": temp_dir}} if use_temp_dir else None
#         processor.preprocess(processed_nb, resources)
#     return True


def run_one(
    fname: Union[Path, str],
    verbose: bool = False,
    timeout: int = 600,
    lib_name: str = None,
    no_run: bool = False,
    pip_install=False,
):
    "Run nb `fname` and timeit, recover exception"
    did_run, skip, error, exec_time = False, False, None, 0
    try:
        # read notebook as dict
        notebook = read_nb(fname)

        # check if notebooks has to be runned
        skip = skip_nb(notebook, lib_name)

        if skip or no_run:
            return _format_row(fname, "skip", exec_time), None
        else:
            did_run, exec_time = exec_nb(fname, pip_install=pip_install)
    except Exception as e:
        if verbose:
            print(f"\nError in {fname}:\n{e}")
            error = e
        error = e
    return (
        _format_row(fname, "ok" if did_run else "fail", exec_time),
        error,
    )


@call_parse
def run_nbs(
    path: Param("A path to nb files", str) = ".",
    verbose: Param("Print errors along the way", store_true) = False,
    timeout: Param("Max runtime for each notebook, in seconds", int) = 600,
    lib_name: Param("Python lib names to filter, eg: tensorflow", str) = None,
    no_run: Param("Do not run any notebook", store_true) = False,
    pip_install: Param("Do not install anything with pip", store_true) = False,
):
    logger = RichLogger(columns=["fname", "status", "t[s]"])
    path = Path(path)
    files = find_nbs(path)

    branch = git_main_name(files[0])

    failed_nbs = {}
    for nb_path in track(files, description="Running nbs..."):
        (fname, run_status, runtime), e = run_one(
            nb_path,
            verbose=verbose,
            timeout=timeout,
            lib_name=lib_name,
            no_run=no_run,
            pip_install=pip_install,
        )
        pprint(f" > {fname:80} | {run_status:40} | {runtime:5} ")
        logger.writerow([fname, run_status, runtime], colab_link=get_colab_url(nb_path, branch))
        time.sleep(0.1)
        if e is not None:
            failed_nbs[str(nb_path)] = e

    logger.to_table()
    logger.to_md("run.md")
    return failed_nbs
