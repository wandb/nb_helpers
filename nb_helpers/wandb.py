# this is for our internal usage
import re
from pathlib import Path
from fastcore.script import Param, call_parse, store_true
from fastcore.basics import listify


from nb_helpers.utils import (
    detect_imported_libs,
    git_local_repo,
    search_string_in_nb,
    read_nb,
    find_nbs,
    RichLogger,
    write_nb,
)
from nb_helpers.colab import add_colab_badge, get_colab_url, has_colab_badge


WANDB_FEATURES = "Table,sweep,WandbCallback,WandbLogger,Artifact"
PYTHON_LIBS = "torch,keras,tensorflow,sklearn,yolo,jax,pandas,numpy,spacy,transformers,lightning,fastai"


def get_wandb_tracker(nb):
    "Get the value inside <!--- @wandbcode{tracker} -->"
    for i, cell in enumerate(nb["cells"]):
        if "@wandbcode" in cell["source"]:
            tracker_id = re.search(r"@wandbcode{(.*?)}", cell["source"]).group(1)
            if i != 0:
                return f'[yellow]{i}: {tracker_id.split(",")[0]}[/yellow]'  # remove the v param
            else:
                return f'[green]{i}: {tracker_id.split(",")[0]}[/green]'  # remove the v param
    return ""


def search_code(nb, features=WANDB_FEATURES):
    "Search notebook for features"
    present_features = []
    for feat in listify(features.split(",")):
        if search_string_in_nb(nb, feat):
            present_features.append(feat)
    return present_features


@call_parse
def summary_nbs(
    path: Param("A path to nb files", str) = ".",
    wandb_features: Param("wandb features to identify, comma separated", str) = WANDB_FEATURES,
    out_file: Param("Export to csv file", Path) = "summary_table.csv",
    github_issue: Param("Creates a `github_issue.md` file ready to be put online", store_true) = True,
):
    path = Path(path)
    # out_file = (path.parent / out_file).with_suffix(".csv")
    logger = RichLogger(
        columns=["#", "nb name", "tracker", "wandb features", "python libs", "colab_cell"], out_file=out_file
    )

    files = find_nbs(path)
    assert len(files) > 0, "There is no `ipynb` notebooks in the path you submited"

    logger.log(f"Reading {len(files)} notebooks")

    repo_path = git_local_repo(files[0])

    for i, nb_path in enumerate(files):
        nb = read_nb(nb_path)
        tracker_id = get_wandb_tracker(nb)
        fname = nb_path.relative_to(repo_path)
        features = search_code(nb, wandb_features)
        libs = detect_imported_libs(nb)
        colab_cell_idx = has_colab_badge(nb)
        row = [
            f"{i+1}",
            str(fname),
            tracker_id,
            ", ".join(features),
            ", ".join(libs),
            str(colab_cell_idx) if colab_cell_idx != -1 else "",
        ]
        colab_link = get_colab_url(nb_path)
        logger.writerow(row, colab_link)
    logger.finish()

    if github_issue:
        logger.create_github_issue()


@call_parse
def fix_nbs(
    path: Param("A path to nb files", str) = ".",
    colab_cell_idx: Param("Cell idx where the colab badge must go", int) = 1,
    branch: Param("The branch", str) = None,
):

    path = Path(path)
    files = find_nbs(path)
    assert len(files) > 0, "There is no `ipynb` notebooks in the path you submited"

    for nb_path in files:
        print(f"Add colab badge to {nb_path}")
        nb = read_nb(nb_path)
        nb = add_colab_badge(nb, nb_path, branch=branch, idx=colab_cell_idx)
        write_nb(nb, nb_path)
