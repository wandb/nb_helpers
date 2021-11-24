import io, json, sys
from pathlib import Path

from nbdev.clean import clean_nb

from nb_helpers.utils import print_output, is_nb, find_nbs

def clean_one(fname: Path, clear_all: bool=False, disp:bool=False):
    """Clean notebook metadata:
    - `clear_all` removes also outputs
    - `disp` prints to stdout
    """
    if not is_nb(fname):
        return
    notebook = json.load(open(fname, "r", encoding="utf-8"))
    clean_nb(notebook, clear_all=clear_all)
    if disp:
        print_output(notebook)
    else:
        x = json.dumps(notebook, sort_keys=True, indent=1, ensure_ascii=False)
        with io.open(fname, "w", encoding="utf-8") as f:
            f.write(x)
            f.write("\n")

def clean_all(path: Path, clear_all=True, disp=False):
    "Apply clean to all nbs inside path recursvely"
    print("\n---------------------------------------------------------------\nStriping notebooks")
    for nb in find_nbs(path):
        print(f"Striping: {nb}")
        clean_one(nb, clear_all, disp)