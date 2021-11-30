import io, json, sys
from pathlib import Path


def is_nb(fname: Path):
    "filter files that are notebooks"
    return (
        (fname.suffix == ".ipynb")
        and (not fname.name.startswith("_"))
        and (not "checkpoint" in str(fname))
    )


def find_nbs(path: Path):
    "Get all nbs on path recursevely"
    return [nb for nb in path.rglob("*.ipynb") if is_nb(nb)]


def print_output(notebook):
    "Print `notebook` in stdout for git things"
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    x = json.dumps(notebook, sort_keys=True, indent=1, ensure_ascii=False)
    output_stream.write(x)
    output_stream.write("\n")
    output_stream.flush()
