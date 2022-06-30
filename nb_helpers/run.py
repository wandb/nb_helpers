import time, os, logging
from pathlib import Path
from typing import Union

from fastcore.script import call_parse, Param, store_true
from rich.progress import Progress

from execnb.nbio import read_nb as read_nb
from execnb.shell import CaptureShell

from nb_helpers.utils import find_nbs, git_main_name, search_string_in_nb, RichLogger
from nb_helpers.colab import get_colab_url


logger = RichLogger(columns=["fname", "status", "t[s]"])

__all__ = ["run_one", "run_nbs"]


def skip_nb(notebook, filters=None):
    "check for notebook filters: tensorflow, pytorch, ..."
    skip = False
    if not search_string_in_nb(notebook, filters):
        skip = True
    return skip


def exec_nb(fname, do_print=False, pip_install=True):
    "Execute tests in notebook in `fn`"
    nb = read_nb(fname)

    def _no_eval(cell):
        if "pip" in cell.source and not pip_install:
            return True
        if cell.cell_type != "code":
            return True
        else:
            return False

    start = time.time()
    k = CaptureShell(fname)
    if do_print:
        logger.info(f"Starting {fname}")
    k.run_all(nb, exc_stop=True, preproc=_no_eval)
    res = True
    if do_print:
        logger.info(f"- Completed {fname}")
    return res, time.time() - start


def run_one(
    fname: Union[Path, str],
    lib_name: str = None,
    no_run: bool = False,
    pip_install=False,
):
    "Run nb `fname` and timeit, recover exception"
    did_run, skip, exception, exec_time = False, False, None, 0
    try:
        # read notebook as dict
        notebook = read_nb(fname)

        # check if notebooks has to be runned
        skip = skip_nb(notebook, lib_name)

        if skip or no_run:
            return (fname, "skip", exec_time), None
        else:
            did_run, exec_time = exec_nb(fname, pip_install=pip_install)
    except Exception as e:
        logger.error(f"Error in {fname}:{e}")
        exception = e
    return (fname, "ok" if did_run else "fail", exec_time), exception


@call_parse
def run_nbs(
    path: Param("A path to nb files", Path, nargs="?", opt=False) = os.getcwd(),
    verbose: Param("Print errors along the way", store_true) = False,
    lib_name: Param("Python lib names to filter, eg: tensorflow", str) = None,
    no_run: Param("Do not run any notebook", store_true) = False,
    pip_install: Param("Do not install anything with pip", store_true) = False,
):
    if verbose:
        logger.logger.setLevel(logging.DEBUG)
    path = Path(path)
    files = find_nbs(path)
    branch = git_main_name(files[0])

    failed_nbs = {}
    with Progress(console=logger.console) as progress:
        task_run_nbs = progress.add_task("Running nbs...", total=len(files))
        for nb_path in files:
            progress.update(task_run_nbs, description=f"Running nb: {str(nb_path.relative_to(nb_path.parent.parent))}")
            (fname, run_status, runtime), e = run_one(
                nb_path,
                lib_name=lib_name,
                no_run=no_run,
                pip_install=pip_install,
            )
            progress.advance(task_run_nbs)
            logger.info(
                f"Executing: {str(fname.relative_to(fname.parent.parent)):50} | {run_status:15} | {int(runtime):5} "
            )
            logger.writerow_incolor(fname, run_status, runtime, colab_link=get_colab_url(nb_path, branch))
            time.sleep(0.1)
            if e is not None:
                failed_nbs[str(nb_path)] = e

    logger.to_table()
    logger.to_md("run.md")
    return failed_nbs
