import io, json, sys, re, csv, fileinput
from types import SimpleNamespace
from typing import Union
from fastcore.foundation import L

from datetime import datetime
import nbformat
from nbformat import NotebookNode
from rich import box
from rich.table import Table
from rich.console import Console
from fastcore.basics import ifnone, listify, store_attr
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
def csv_to_md(csv_file_path, delimiter=";"):
    "From csv file to markdown table, useful for github posting"
    output_file = Path(csv_file_path).with_suffix(".md")
    csv_dict = csv.DictReader(open(csv_file_path, encoding="UTF-8"), delimiter=delimiter)
    list_of_rows = [dict_row for dict_row in csv_dict]
    headers = list(list_of_rows[0].keys())
    md_string = " | "
    for header in headers:
        md_string += header + " |"

    md_string += "\n |"
    for i in range(len(headers)):
        md_string += "--- | "

    md_string += "\n"
    for row in list_of_rows:
        md_string += " | "
        for header in headers:
            md_string += row[header] + " | "
        md_string += "\n"

    # writing md_string to the output_file
    file = open(output_file, "w", encoding="UTF-8")
    file.write(md_string)
    file.close()

    print("The markdown file has been created!!!")


class RichLogger:
    "A simple logger that logs to a file and the rich console"

    def __init__(
        self, columns=["#", "name"], colab=True, out_file="summary_table.csv", delimiter=";", width=180, md=True
    ):
        self.console = Console(width=width, record=True)
        print(f"CONSOLE.is_terminal(): {self.console.is_terminal}")

        # beautiful rich table
        store_attr()
        columns = columns + (["colab"] if colab else [])
        self.table = create_table(columns=columns)
        self.log(f"Writing output to {out_file}")
        self.csv_file = open(out_file, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file, delimiter=delimiter)
        self.csv_writer.writerow(columns)

    def log(self, text):
        self.console.print(text)

    @staticmethod
    def _format_colab_link(colab_link):
        return f"[link={colab_link}]open[link]"

    @staticmethod
    def _format_colab_link_md(colab_link):
        return f"[open]({colab_link})"

    def writerow(self, row, colab_link=None):
        self.csv_writer.writerow([remove_rich_format(e) for e in row] + [self._format_colab_link_md(colab_link)])
        row = list(row) + [self._format_colab_link(colab_link)]
        self.table.add_row(*row)

    def finish(self):
        self.csv_file.close()
        if self.md:
            csv_to_md(self.out_file, delimiter=self.delimiter)
        self.console.print(self.table)
        self.console.print("END!")

    def create_github_issue(self, github_issue_file="github_issue.md", table=True, message=None):
        github_issue_file = Path(github_issue_file)
        with open(github_issue_file, "w", encoding="utf-8") as file:
            header = (
                f"# Summary: {today()}\n"
                "> This file was created automatically!\n\n"
                "To generate this table run:\n"
                "```bash\n$ nb_helpers.summary_nbs --path=tests\n```\n"
            )
            file.write(header)
            if table:
                table = open("summary_table.md", encoding="utf-8")
                file.write(table.read())
                table.close()
            if message is not None:
                file.write(message)


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


def search_cells(nb, string: str = None, cell_type=CellType.code):
    "Get cells containing string, you can pass comma separated strings"
    strings = ifnone(string, "").replace(" ", "").split(",")
    cells = []
    for cell in nb["cells"]:
        if cell["cell_type"] == cell_type:
            if any([string in cell["source"] for string in strings]):
                cells.append(cell["source"])
    return cells


def search_string_in_nb(nb, string: str = None, cell_type=CellType.code):
    "Check if string is present in notebook cells, you can pass comma separated strings"
    return len(search_cells(nb, string, cell_type)) > 0


def extract_libs(strings):
    "Automatically detect libraries imported in `strings`"

    after_import_regex = re.compile(r"^import\s([^\.]*)", re.VERBOSE)
    before_as_regex = re.compile(r"([^\s]*?)\sas\s", re.VERBOSE)
    between_from_import_regex = re.compile(r"^from\s(.*?)\simport", re.VERBOSE)

    def _search_with_regex(regex, string):
        res = regex.search(string)
        if res is not None:
            return res.group(1)
        else:
            return ""

    libs = []
    for string in strings:
        if "from" in string:
            string = _search_with_regex(between_from_import_regex, string).split(".")[0]
        else:
            string = _search_with_regex(after_import_regex, string)
            if "as" in string:
                string = _search_with_regex(before_as_regex, string)
        libs.append(string.replace(" ", "").split(","))
    return L(libs).concat()


def detect_imported_libs(notebook):
    "Guess imported libs from notebook"
    text_list = search_cells(notebook, "import,from")

    # format lines
    text_list = L([x.split("\n") for x in text_list]).concat()
    text_list = [line for line in text_list if (("from" in line) or ("import" in line))]

    return extract_libs(text_list)


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


def today():
    "datetime object containing current date and time"
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string
