from pathlib import Path
from IPython import get_ipython
from fastcore.basics import ifnone

import nbformat

from nb_helpers.utils import git_main_name, git_origin_repo, read_nb, git_local_repo

## colab
def in_colab():
    "Check if we are in Colab"
    if "google.colab" in str(get_ipython()):  # pragma: no cover
        return True
    return False


def get_colab_url(fname, branch="main"):
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


_badge_meta = {"id": "view-in-github", "colab_type": "text"}


def _create_colab_cell(url, meta={}):
    "Creates a notebook cell with the `Open In Colab` badge"
    kwargs = {
        "cell_type": "markdown",
        "metadata": meta,
        "source": f'<a href="{url}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>',
    }
    return _new_cell("markdown", **kwargs)


def has_colab_badge(nb):
    "Check if notebook has colab badge, returns the cell position, -1 if not present"
    for i, cell in enumerate(nb["cells"]):
        if "Open In Colab" in cell["source"]:
            return i
    return -1


def create_colab_badge_cell(fname, branch=None, meta={}):
    "Create a colab badge cell from `fname`"
    # get main/master name
    branch = ifnone(branch, git_main_name(fname))
    url = get_colab_url(fname, branch)
    colab_cell = _create_colab_cell(url, meta)
    return colab_cell


def add_colab_badge(notebook, fname, branch=None, idx=0, meta={}):
    "Add a badge to Open In Colab in the `idx` cell"
    idx_colab_badge = has_colab_badge(notebook)
    if idx_colab_badge != -1:
        colab_cell = notebook["cells"].pop(idx_colab_badge)
    else:
        colab_cell = create_colab_badge_cell(fname, branch, meta)
    notebook["cells"].insert(idx, colab_cell)
    return notebook
