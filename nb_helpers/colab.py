from pathlib import Path
from IPython import get_ipython

import nbformat

from nb_helpers.utils import git_origin_repo, read_nb, git_local_repo

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


def _create_colab_cell(url):
    "Creates a notebook cell with the `Open In Colab` badge"
    kwargs = {
        "metadata": {"colab_type": "text", "id": "view-in-github"},
        "source": f'<a href="{url}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>',
    }
    return _new_cell("markdown", **kwargs)


def _has_colab_badge(nb):
    "Check if notebook has colab badge, returns the cell position"
    for i, cell in enumerate(nb["cells"]):
        if "Open In Colab" in cell["source"]:
            return i
    return -1

_badge_meta = {"id": "view-in-github", "colab_type": "text"}

def _add_colab_metadata(cell, meta=_badge_meta):
    "Fix colab badge metadata"
    if "Open In Colab" in cell["source"]:
        cell["metadata"] = meta
    return cell


def add_colab_badge(fname, branch="main", idx=0, meta=_badge_meta):
    "Add a badge to Open In Colab in the `idx` cell"
    notebook = read_nb(fname)
    url = get_colab_url(fname, branch)
    idx_colab_badge = _has_colab_badge(notebook)
    if idx_colab_badge != -1:
        colab_cell = notebook["cells"].pop(idx_colab_badge)
    else:
        colab_cell = _create_colab_cell(url)
    if meta:
        colab_cell = _add_colab_metadata(colab_cell, _badge_meta)
    notebook["cells"].insert(idx, colab_cell)
    return notebook
