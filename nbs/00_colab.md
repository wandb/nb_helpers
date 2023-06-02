
```python
#| default_exp colab
```


[**Try in a Colab Notebook here →**](https://colab.research.google.com/github/wandb/nb_helpers/blob/master/nbs/00_colab.ipynb)

# Google Colab utils
> Deal with colab specific format

```python
#| export
from pathlib import Path
from IPython import get_ipython
from IPython.display import display, Markdown

from fastcore.basics import ifnone

from execnb.nbio import NbCell, read_nb

from nb_helpers.utils import git_main_name, git_origin_repo, git_local_repo, search_cell, git_current_branch
```


```python
this_nb = Path("00_colab.ipynb")
notebook = read_nb(this_nb)
```


```python
this_nb.resolve()
```


```python
git_origin_repo(this_nb.resolve())
```


```python
#| export
def get_colab_url(fname, branch):
    "Get git repo url, to append to colab"
    fname = Path(fname).resolve()
    github_repo = git_origin_repo(fname)
    fname = fname.relative_to(git_local_repo(fname))

    return f"https://colab.research.google.com/github/{github_repo}/blob/{branch}/{str(fname)}"
```


```python
get_colab_url(this_nb, branch="master")
```


```python
#| exporti
_badge_meta = {"id": "view-in-github", "colab_type": "text"}
```


```python
#| export
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
```


```python
url = get_colab_url(this_nb, branch="master")
cell = _create_colab_cell(url)
display(Markdown(cell["source"]))
```


```python
#| export
def has_colab_badge(nb):
    "Check if notebook has colab badge, returns the cell position, -1 if not present"
    for i, cell in enumerate(nb["cells"]):
        if search_cell(cell, "Open In Colab"):
            return i
    return -1
```


```python
assert has_colab_badge(notebook) == 0
```


```python
#| export
def create_colab_badge_cell(fname, branch=None, meta={}, tracker=None):
    "Create a colab badge cell from `fname`"
    # get main/master name
    branch = ifnone(branch, git_main_name(fname))
    url = get_colab_url(fname, branch)
    colab_cell = _create_colab_cell(url, meta, tracker)
    return colab_cell
```


```python
create_colab_badge_cell(this_nb)
```


```python
#| export
def add_colab_badge(notebook, fname, branch=None, idx=0, meta=_badge_meta, tracker=None):
    "Add a badge to Open In Colab in the `idx` cell"
    idx_colab_badge = has_colab_badge(notebook)
    if idx_colab_badge != -1:
        notebook["cells"].pop(idx_colab_badge)
    colab_cell = create_colab_badge_cell(fname, branch, meta, tracker)
    notebook["cells"].insert(idx, colab_cell)
    return notebook
```


```python
nb_with_colab_badge = add_colab_badge(notebook, fname=this_nb)
```

it should have the colab badge in the first cell now

```python
assert has_colab_badge(nb_with_colab_badge) == 0
```

Let's also activate the GPU on colab

```python
d = dict(a=1, b=2)
```


```python
d.update({"c": 3})
```


```python
#| exporti
_colab_meta = {
    "colab": {
        "include_colab_link": True, 
        "toc_visible": True,
        "provenance": []
        },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
      },
    "language_info": {
      "name": "python"
      },
    "accelerator": "GPU",
    "gpuClass": "standard"
    }

```


```python
#| export
def add_colab_metadata(notebook, meta=_colab_meta):
    "Adds GPU and colab meta to `notebook`"
    if "accelerator" in notebook: # old colaboratory standard
        del notebook["accelerator"]
    notebook["metadata"].update(_colab_meta)
    return notebook
```


```python
add_colab_metadata(notebook)["metadata"]
```

## Export -

```python
#|hide
from nbdev import *
nbdev_export()
```

