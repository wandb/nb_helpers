from pathlib import Path
from IPython import get_ipython
from fastcore.basics import ifnone

from execnb.nbio import NbCell

from nb_helpers.utils import git_main_name, git_origin_repo, git_local_repo, search_cell


def get_colab_url(fname, branch="main"):
    "Get git repo url, to append to colab"
    fname = Path(fname)
    github_repo = git_origin_repo(fname)
    fname = fname.relative_to(git_local_repo(fname))
    return f"https://colab.research.google.com/github/{github_repo}/blob/{branch}/{str(fname)}"


_badge_meta = {"id": "view-in-github", "colab_type": "text"}


def _create_colab_cell(url, meta={}, tracker=None):
    "Creates a notebook cell with the `Open In Colab` badge"
    tracker = ifnone(tracker, "")
    data = {
        "cell_type": "markdown",
        "metadata": meta,
        "source": f'<a href="{url}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>\n'
        + tracker,
    }
    return NbCell(-1, data)


def has_colab_badge(nb):
    "Check if notebook has colab badge, returns the cell position, -1 if not present"
    for i, cell in enumerate(nb["cells"]):
        if search_cell(cell, "Open In Colab"):
            return i
    return -1


def create_colab_badge_cell(fname, branch=None, meta={}, tracker=None):
    "Create a colab badge cell from `fname`"
    # get main/master name
    branch = ifnone(branch, git_main_name(fname))
    url = get_colab_url(fname, branch)
    colab_cell = _create_colab_cell(url, meta, tracker)
    return colab_cell


def add_colab_badge(notebook, fname, branch=None, idx=0, meta=_badge_meta, tracker=None):
    "Add a badge to Open In Colab in the `idx` cell"
    idx_colab_badge = has_colab_badge(notebook)
    if idx_colab_badge != -1:
        notebook["cells"].pop(idx_colab_badge)
    colab_cell = create_colab_badge_cell(fname, branch, meta, tracker)
    notebook["cells"].insert(idx, colab_cell)
    return notebook


_colab_meta = {
    "accelerator": "GPU",
    "colab": {"include_colab_link": True, "toc_visible": True},
}


def add_colab_metadata(notebook, meta=_colab_meta):
    "Adds GPU and colab meta to `notebook`"
    notebook["metadata"].update(_colab_meta)
    return notebook
