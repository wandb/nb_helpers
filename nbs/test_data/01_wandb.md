
```python
#| default_exp wandb
```



[![Run in Google Colab](https://www.tensorflow.org/images/colab_logo_32px.png)](https://colab.research.google.com/github/wandb/nb_helpers/blob/master/nbs/01_wandb.ipynb) [Run in Google Colab](https://colab.research.google.com/github/wandb/nb_helpers/blob/master/nbs/01_wandb.ipynb) &nbsp; [![View source on GitHub](https://www.tensorflow.org/images/GitHub-Mark-32px.png)](https://github.com/wandb/nb_helpers/blob/main/nbs/01_wandb.ipynb) [View source on GitHub](https://github.com/wandb/nb_helpers/blob/main/nbs/01_wandb.ipynb)

# Weights and Biases specifics
> To deal with wandb specific usage for our examples repo https://github.com/wandb/examples

```python
#| export
import re, os
from pathlib import Path
from tempfile import TemporaryDirectory

from fastcore.script import Param, call_parse, store_true
from fastcore.basics import listify

from execnb.nbio import read_nb, write_nb

from nb_helpers.utils import (
    detect_imported_libs,
    git_main_name,
    search_string_in_nb,
    find_nbs,
    RichLogger,
    git_local_repo,
)
from nb_helpers.clean import clean_nb, clean_one
from nb_helpers.colab import add_colab_badge, add_colab_metadata, get_colab_url, has_colab_badge
```


```python
this_nb = Path("01_wandb.ipynb")
notebook = read_nb(this_nb)
```


```python
#| export
WANDB_FEATURES = "Table,sweep,WandbCallback,WandbLogger,Artifact"
```


```python
#| export
PYTHON_LIBS = "torch,keras,tensorflow,sklearn,yolo,jax,pandas,numpy,spacy,transformers,lightning,fastai"
```


```python
#| export
def get_wandb_tracker(nb):
    "Get the value inside <!--- @wandbcode{tracker} -->"
    for cell in nb["cells"]:
        if "@wandbcode" in cell["source"]:
            match = re.search(r"@wandbcode{(.*?)}", cell["source"])
            if match is not None:
                tracker_id = match.group(1)  
                return tracker_id.split(",")[0]
    return ""
```


```python
assert get_wandb_tracker(notebook) == "tracker"
```


```python
#| export
def search_code(nb, features=WANDB_FEATURES):
    "Search notebook for features"
    present_features = []
    for feat in listify(features.split(",")):
        if search_string_in_nb(nb, feat):
            present_features.append(feat)
    return present_features
```


```python
search_code(notebook)
```


```python
#| export
@call_parse
def summary_nbs(
    path: Param("A path to nb files", Path, nargs="?", opt=False) = os.getcwd(),
    wandb_features: Param("wandb features to identify, comma separated", str) = WANDB_FEATURES,
    out_file: Param("Export to csv file", Path) = "summary_table.csv",
    full_path: Param("Use full path for fname", store_true) = False,
):
    path = Path(path)
    # out_file = (path.parent / out_file).with_suffix(".csv")
    logger = RichLogger(columns=["fname", "tracker", "wandb", "python libs", "colab_idx"], out_file=out_file)

    files = find_nbs(path)
    assert len(files) > 0, "There is no `ipynb` notebooks in the path you submited"

    logger.info(f"Reading {len(files)} notebooks")

    repo_path = git_local_repo(files[0])
    branch = git_main_name(repo_path)

    for nb_path in files:
        print(nb_path)
        nb = read_nb(nb_path)
        tracker_id = get_wandb_tracker(nb)
        fname = nb_path.name if not full_path else nb_path.relative_to(repo_path)
        features = search_code(nb, wandb_features)
        libs = detect_imported_libs(nb)
        colab_cell_idx = has_colab_badge(nb)
        row = [
            str(fname),
            tracker_id,
            ", ".join(features),
            ", ".join(libs),
            str(colab_cell_idx) if colab_cell_idx != -1 else "",
        ]
        colab_link = get_colab_url(nb_path, branch)
        logger.writerow(row, colab_link)
    logger.to_table()
    logger.to_csv(Path(out_file).with_suffix(".csv"))
    logger.to_md(Path(out_file).with_suffix(".md"))
```


```python
with TemporaryDirectory() as d:
    summary_nbs(out_file=Path(d)/"summary.csv")
```


```python
#| export
@call_parse
def fix_nbs(
    path: Param("A path to nb files", Path, nargs="?", opt=False) = os.getcwd(),
    colab_cell_idx: Param("Cell idx where the colab badge must go", int) = 0,
    branch: Param("The branch", str) = None,
):

    path = Path(path)
    files = find_nbs(path)
    assert len(files) > 0, "There is no `ipynb` notebooks in the path you submited"

    for nb_path in files:
        print(f"Add colab badge to {nb_path}")
        clean_one(nb_path, clear_outs=True)
        nb = read_nb(nb_path)
        tracker = get_wandb_tracker(nb)
        if tracker is not None and tracker != "":
            tracker = f"<!--- @wandbcode{{{tracker}}} -->"
        nb = add_colab_badge(nb, nb_path, branch=branch, idx=colab_cell_idx, tracker=tracker)
        add_colab_metadata(nb)
        clean_nb(nb)
        write_nb(nb, nb_path)
```

let's make sure that every notebooks has a `open in colab` badge

```python
#|eval: false
fix_nbs()
```

We may want to check what libs are in use:

```python
#| export
@call_parse
def filter_nbs(
    path: Param("A path to nb files", Path, nargs="?", opt=False) = os.getcwd(),
    lib_name: Param("Python lib names to filter, eg: tensorflow", str) = "",
    out_file: Param("Export to csv file", Path) = "filtered_nbs.csv",
):

    path = Path(path)

    logger = RichLogger(columns=["fname", "python libs"], out_file=out_file)

    files = find_nbs(path)
    assert len(files) > 0, "There is no `ipynb` notebooks in the path you submited"

    repo_path = git_local_repo(files[0])

    for nb_path in files:
        nb = read_nb(nb_path)
        fname = nb_path.relative_to(repo_path)
        libs = ", ".join(detect_imported_libs(nb))
        if lib_name in libs:
            row = [str(fname), libs]
            logger.writerow(row)

    logger.to_table()
    logger.to_csv(Path(out_file).with_suffix(".csv"), format_link=False)
```


```python
with TemporaryDirectory() as d:
    filter_nbs(out_file=Path(d)/"summary.csv")
```

