import io, json, sys, re
from types import SimpleNamespace
from typing import Union
from fastcore.foundation import L

import nbformat
from nbformat import NotebookNode
from rich.table import Table
from IPython import get_ipython
from fastcore.basics import ifnone, listify
from fastcore.xtras import run
from pathlib import Path


# rich
def create_table(columns=["Notebook Path", "Status", "Run Time", "Colab"], xtra_cols=None) -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    for col in columns + listify(xtra_cols):
        table.add_column(col)
    return table


def remove_rich_format(text):
    "Remove rich fancy coloring"
    res = re.search(r"\](.*?)\[", text)
    if res is None:
        return text
    else:
        return res.group(1)


# nb
def is_nb(fname: Path):
    "filter files that are jupyter notebooks"
    return (fname.suffix == ".ipynb") and (not fname.name.startswith("_")) and (not "checkpoint" in str(fname))


def find_nbs(path: Path):
    "Get all nbs on path recursevely"
    return L([nb for nb in path.rglob("*.ipynb") if is_nb(nb)]).sorted()

def print_output(notebook):  # pragma: no cover
    "Print `notebook` in stdout for git things"
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    x = json.dumps(notebook, sort_keys=True, indent=1, ensure_ascii=False)
    output_stream.write(x)
    output_stream.write("\n")
    output_stream.flush()


def read_nb(fname: Union[Path, str]) -> NotebookNode:
    "Read the notebook in `fname`."
    with open(Path(fname), "r", encoding="utf8") as f:
        return nbformat.reads(f.read(), as_version=4)


CellType = SimpleNamespace(code="code", md="markdown")


def search_string_in_nb(nb, string: str = None, cell_type=CellType.code):
    "Search string in notebook code cells, you can pass comma separated strings"
    strings = ifnone(string, "").split(",")
    for cell in nb["cells"]:
        if cell["cell_type"] == cell_type:
            for string in strings:
                if string in cell["source"]:
                    return True
    return False


## colab
def is_colab():
    if "google.colab" in str(get_ipython()):  # pragma: no cover
        return True
    return False


## Git
def git_current_branch():
    "Get current git branch"
    return run("git symbolic-ref --short HEAD")


def git_origin_repo():
    "Get git repo url, to append to colab"
    try:
        repo_url = run("git config --get remote.origin.url")
        # check if ssh or html
        if "git@" in repo_url:
            github_repo = re.search(r":(.*?).git", repo_url).group(1)
            return f"github/{github_repo}/blob/{git_current_branch()}"
        else:
            github_repo = re.search(r".com/(.*)", repo_url).group(1)
            return f"github/{github_repo}/blob/{git_current_branch()}"
    except:
        print("Probably not in a git repo\n")
        return ""
