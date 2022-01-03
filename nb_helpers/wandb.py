# this is for our internal usage
import csv
import re
from pathlib import Path
from fastcore.script import Param, call_parse, store_true
from fastcore.basics import listify


from rich import print
from rich.console import Console

from nb_helpers.utils import create_table, remove_rich_format, search_string_in_nb, is_nb, read_nb, find_nbs


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
    console = Console(width=180)
    print(f"CONSOLE.is_terminal(): {console.is_terminal}")
    path = Path(path)
    if is_nb(path):
        files = [path]
    else:
        files = find_nbs(path)
    print(f"Reading {len(files)} notebooks")

    out_file = (path.parent / out_file).with_suffix(".csv")
    with open(out_file, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";")
        print(f"Writing output to {out_file}")
        csv_writer.writerow(["#", "nb name", "tracker", "wandb features", "python libs"])

        # a beautiful rich terminal table
        table = create_table(["#", "nb name", "tracker", "wandb features", "python libs"])

        for i, nb_path in enumerate(files):
            nb = read_nb(nb_path)
            tracker_id = get_wandb_tracker(nb)
            fname = nb_path.relative_to(nb_path.parent.parent)
            features = _search_code(nb, wandb_features)
            libs = _search_code(nb, python_libs)
            csv_writer.writerow(
                [f"{i+1}", str(fname), remove_rich_format(tracker_id), "-".join(features), "-".join(libs)]
            )
            table.add_row(f"{i+1}", str(fname), tracker_id, ", ".join(features), ", ".join(libs))
        console.print(table)
        console.print("END!")
