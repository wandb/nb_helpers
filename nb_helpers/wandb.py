# this is for our internal usage
import re
from pathlib import Path
from fastcore.script import Param, call_parse
from fastcore.basics import listify

from nb_helpers.utils import git_local_repo, search_string_in_nb, is_nb, read_nb, find_nbs, Logger
from nb_helpers.colab import get_colab_url


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


def _search_code(nb, features=WANDB_FEATURES):
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
    python_libs: Param("Python lib names to filter, eg: tensorflow. Comma separated", str) = PYTHON_LIBS,
    out_file: Param("Export to csv file", Path) = "summary.csv",
):
    path = Path(path)
    out_file = (path.parent / out_file).with_suffix(".csv")
    logger = Logger(columns=["#", "nb name", "tracker", "wandb features", "python libs"], out_file=out_file)
    
    files = find_nbs(path)
    assert len(files)>0, "There is no `ipynb` notebooks in the path you submited"

    logger.log(f"Reading {len(files)} notebooks")

    repo_path = git_local_repo(files[0])

    for i, nb_path in enumerate(files):
        nb = read_nb(nb_path)
        tracker_id = get_wandb_tracker(nb)
        fname = nb_path.relative_to(repo_path)
        features = _search_code(nb, wandb_features)
        libs = _search_code(nb, python_libs)
        
        row = [f"{i+1}", str(fname), tracker_id, ", ".join(features), ", ".join(libs)]
        colab_link = get_colab_url(nb_path)
        logger.writerow(row, colab_link)
    
    logger.finish()

