import io, json, sys, re, csv
from types import SimpleNamespace
from typing import Union
from fastcore.foundation import L

import nbformat
from nbformat import NotebookNode
from rich import box
from rich.table import Table
from rich.console import Console
from fastcore.basics import ifnone, listify
from fastcore.xtras import run
from pathlib import Path


# rich
def create_table(columns=["Notebook Path", "Status", "Run Time", "Colab"], xtra_cols=None) -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.box = box.SQUARE

    table.border_style = "bright_yellow"
    table.row_styles = ["none", "dim"]
    for col in columns + listify(xtra_cols):
        table.add_column(col)
    table.columns[1].style = "cyan"
    return table


def remove_rich_format(text):
    "Remove rich fancy coloring"
    text = str(text)
    res = re.search(r"\](.*?)\[", text)
    if res is None:
        return text
    else:
        return res.group(1)


# log
class RichLogger:
    "A simple logger that logs to a file and the rich console"

    def __init__(self, columns=["#", "name"], colab=True, out_file="summary.csv", delimiter=";", width=180):
        self.console = Console(width=width)
        print(f"CONSOLE.is_terminal(): {self.console.is_terminal}")

        # beautiful rich table
        self.table = create_table(columns + (["colab"] if colab else []))

        # outfile setup
        logs_folder = git_local_repo(list(Path.cwd().iterdir())[0]) / "logs"
        if not logs_folder.exists():
            logs_folder.mkdir()
        out_file = logs_folder / out_file
        self.log(f"Writing output to {out_file}")
        self.csv_file = open(out_file, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file, delimiter=delimiter)
        self.csv_writer.writerow(columns)

    def log(self, text):
        self.console.print(text)

    @staticmethod
    def _format_colab_link(colab_link):
        return f"[link={colab_link}]open[link]"

    def writerow(self, row, colab_link=None):
        self.csv_writer.writerow([remove_rich_format(e) for e in row])
        row = list(row) + [self._format_colab_link(colab_link)]
        self.table.add_row(*row)

    def finish(self):
        self.csv_file.close()
        self.console.print(self.table)
        self.console.print("END!")


# nb
def is_nb(fname: Path):
    "filter files that are jupyter notebooks"
    return (fname.suffix == ".ipynb") and (not fname.name.startswith("_")) and (not "checkpoint" in str(fname))


def find_nbs(path: Path):
    "Get all nbs on path recursevely"
    path = Path(path)
    if is_nb(path):
        return [path]
    return L([nb for nb in path.rglob("*.ipynb") if is_nb(nb)]).sorted()


def print_output(notebook):  # pragma: no cover
    "Print `notebook` in stdout for git things"
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    x = json.dumps(notebook, sort_keys=True, indent=1, ensure_ascii=False)
    output_stream.write(x)
    output_stream.write("\n")
    output_stream.flush()


def read_nb(fname: Union[Path, str]) -> NotebookNode:
    "Read the notebook in `fname`."
    with open(Path(fname), "r", encoding="utf8") as f:
        return nbformat.reads(f.read(), as_version=4)


def write_nb(notebook, fname: Union[Path, str]):
    "Dump `notebook` to `fname`"
    nbformat.write(notebook, str(fname), version=4)


CellType = SimpleNamespace(code="code", md="markdown")


def search_string_in_nb(nb, string: str = None, cell_type=CellType.code):
    "Search string in notebook code cells, you can pass comma separated strings"
    strings = ifnone(string, "").split(",")
    for cell in nb["cells"]:
        if cell["cell_type"] == cell_type:
            for string in strings:
                if string in cell["source"]:
                    return True
    return False


## Git
def git_current_branch(fname):
    "Get current git branch"
    return run(f"git -C {Path(fname).parent} symbolic-ref --short HEAD")


def git_main_name(fname):
    "Get the name of master/main branch"
    branches = run(f"git -C {Path(fname).parent} branch")
    return "main" if "main" in branches else "master"


def git_origin_repo(fname):
    "Get github repo name from `fname`"
    try:
        repo_url = run(f"git -C {Path(fname).parent} config --get remote.origin.url")

        # check if ssh or html
        if "git@" in repo_url:
            github_repo = re.search(r":(.*?).git", repo_url).group(1)
        else:
            github_repo = re.search(r".com/(.*)", repo_url).group(1)
        return github_repo

    except Exception as e:
        print(f"Probably not in a git repo: {e}")
        return ""


def git_local_repo(fname):
    "Get local github repo path"
    fname = Path(fname)
    repo = git_origin_repo(fname)
    for p in fname.parents:
        if p.match(f"*/{repo}"):
            break
    return p


def git_last_commit(fname, branch="master"):
    "Gets the last commit on fname"
    commit_id = run(f"git rev-list -1 {branch} {fname}")
    return commit_id
