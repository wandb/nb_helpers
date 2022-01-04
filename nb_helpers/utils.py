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

def save_nb(notebook, fname: Union[Path, str]):
    "Dump `notebook` to `fname`"
    nbformat.write(notebook, str(fname), version=4)


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




## Git
def git_current_branch(fname):
    "Get current git branch"
    return run(f"git -C {Path(fname).parent} symbolic-ref --short HEAD")

def git_origin_repo(fname):
    "Get github repo name from `fname`"
    try:
        repo_url = run(f"git -C {Path(fname).parent} config --get remote.origin.url")
        
        # check if ssh or html
        if "git@" in repo_url:
            github_repo = re.search(r":(.*?).git", repo_url).group(1)
        else:
            github_repo = re.search(r".com/(.*)", repo_url).group(1)
        return github_repo

    except Exception as e:
        print(f"Probably not in a git repo: {e}")
        return ""

def git_local_repo(fname):
    "Get local github repo path"
    repo = git_origin_repo(fname)
    for p in fname.parents:
        if p.match(f'*/{repo}'):
            break
    return p


## colab
def is_colab():
    "Check if we are in Colab"
    if "google.colab" in str(get_ipython()):  # pragma: no cover
        return True
    return False

def get_colab_url(fname, branch='main'):
    "Get git repo url, to append to colab"
    fname = Path(fname)
    github_repo = git_origin_repo(fname)
    fname = fname.relative_to(git_local_repo(fname))
    return f"https://colab.research.google.com/github/{github_repo}/blob/{branch}/{str(fname)}"


def _new_cell(type="code", **kwargs):
    "Add V4 nbformat type cell"
    if type == "code":
        return nbformat.v4.new_code_cell(**kwargs)
    if type == "markdown":
        return nbformat.v4.new_markdown_cell(**kwargs)

def _create_colab_cell(url):
    "Creates a notebook cell with the `Open In Colab` badge"
    kwargs = {
        'metadata': {'colab_type': 'text', 'id': 'view-in-github'},
        'source': f'<a href="{url}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>'
        }
    return _new_cell("markdown", **kwargs)

def _has_colab_badge(nb):
    "Check if notebook has colab badge, returns the cell position"
    for i, cell in enumerate(nb["cells"]):
        if "Open In Colab" in cell["source"]:
            return i
    return -1

def _fix_colab_badge(cell):
    "Fix colab badge metadata"
    if "Open In Colab" in cell["source"]:
        cell["metadata"] = {'id': 'view-in-github', 'colab_type': 'text'}
    return cell

def add_colab_badge(fname, branch='main', idx=0):
    "Add a badge to Open In Colab in the first cell"
    notebook = read_nb(fname)
    url = get_colab_url(fname, branch)
    idx_colab_badge = _has_colab_badge(notebook)
    if idx_colab_badge!=-1:
        colab_cell = notebook["cells"].pop(idx_colab_badge)
    else:
        colab_cell = _create_colab_cell(url)
    colab_cell = _fix_colab_badge(colab_cell)
    notebook["cells"].insert(idx, colab_cell)
    return notebook
