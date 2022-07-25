import time, os, logging, re
from pathlib import Path
from typing import Union

from fastcore.basics import patch
from fastcore.script import call_parse, Param, store_true
from rich.progress import Progress

from execnb.nbio import read_nb
from execnb.shell import *
from nb_helpers.actions import create_issue_nb_fail

from nb_helpers.utils import find_nbs, git_main_name, search_string_in_nb, RichLogger
from nb_helpers.colab import get_colab_url


logger = RichLogger(columns=["fname", "status", "t[s]"])

__all__ = ["exec_nb", "run_one", "run_nbs"]


def skip_nb(notebook, filters=None):
    "check for notebook filters: tensorflow, pytorch, ..."
    skip = False
    if not search_string_in_nb(notebook, filters):
        skip = True
    return skip


def exec_nb(fname, pip_install=True):
    "Execute tests in notebook in `fn`"
    nb = read_nb(fname)

    def preproc(cell):
        logger.info(cell.source)
        if ("!pip install" in cell.source and not pip_install) and cell.cell_type == "code":
            return True
        if cell.cell_type != "code":
            return True
        else:
            return False

    shell = CaptureShell(fname)
    try:
        shell.run_all(nb, exc_stop=True, preproc=preproc)
    except Exception as e:
        return False, shell
    return True, shell


@patch
def prettytb(
    self: CaptureShell, fname: Union[Path, str] = None, simple=False
):  # filename to print alongside the traceback
    "Show a pretty traceback for notebooks, optionally printing `fname`."
    fname = fname if fname else self._fname
    _fence = "=" * 75
    cell_intro_str = f"While Executing Cell #{self._cell_idx}:" if self._cell_idx else "While Executing:"
    cell_str = f"\n{cell_intro_str}\n{self.exc[-1]}"
    fname_str = f" in {fname}" if fname else ""
    res = f"{type(self.exc[1]).__name__}{fname_str}:\n{_fence}\n{cell_str}\n"
    if simple:
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        res = ansi_escape.sub("", res)
    return res


def run_one(
    fname: Union[Path, str],
    lib_name: str = None,
    no_run: bool = False,
    pip_install=False,
    github_issue=False,
    repo=None,
    owner=None,
):
    "Run nb `fname` and timeit, recover exception"
    did_run, skip, exec_time = False, False, time.time()

    # read notebook as dict
    notebook = read_nb(fname)

    # check if notebooks has to be runned
    skip = skip_nb(notebook, lib_name)

    if skip or no_run:
        return "skip", 0
    else:
        did_run, shell = exec_nb(fname, pip_install=pip_install)
    if shell.exc:
        print(shell.prettytb(fname))
        logger.error(f"Error in {fname}:{shell.exc[1]}")
        if github_issue:
            create_issue_nb_fail(fname, shell.prettytb(fname, simple=True), repo=repo, owner=owner)
    return "ok" if did_run else "fail", time.time() - exec_time


@call_parse
def run_nbs(
    path: Param("A path to nb files", Path, nargs="?", opt=False) = os.getcwd(),
    verbose: Param("Print errors along the way", store_true) = False,
    lib_name: Param("Python lib names to filter, eg: tensorflow", str) = None,
    no_run: Param("Do not run any notebook", store_true) = False,
    pip_install: Param("Run cells with !pip install", store_true) = False,
    github_issue: Param("Create a github issue if notebook fails", store_true) = False,
    repo: Param("Github repo to create issue in", str) = None,
    owner: Param("Github owner to create issue in", str) = None,
):
    if verbose:
        logger.logger.setLevel(logging.DEBUG)
    path = Path(path)
    files = find_nbs(path)
    branch = git_main_name(files[0])

    with Progress(console=logger.console) as progress:
        task_run_nbs = progress.add_task("Running nbs...", total=len(files))
        for fname in files:
            progress.update(task_run_nbs, description=f"Running nb: {str(fname.relative_to(fname.parent.parent))}")
            (run_status, runtime) = run_one(
                fname,
                lib_name=lib_name,
                no_run=no_run,
                pip_install=pip_install,
                github_issue=github_issue,
                repo=repo,
                owner=owner,
            )
            progress.advance(task_run_nbs)
            logger.writerow_incolor(fname, run_status, runtime, colab_link=get_colab_url(fname, branch))
            time.sleep(0.1)

    logger.to_table()
    logger.to_md("run.md")
    return
