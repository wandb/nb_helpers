# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_utils.ipynb.

# %% auto 0
__all__ = ['LOGFORMAT', 'LOGFORMAT_RICH', 'STATUS', 'CellType', 'create_table', 'remove_rich_format', 'csv_to_md', 'RichLogger',
           'is_nb', 'load_list_from_file', 'load_notebooks_from_file', 'find_nbs', 'print_output', 'search_cell',
           'search_cells', 'search_string_in_nb', 'extract_libs', 'detect_imported_libs', 'get_repo',
           'git_current_branch', 'git_branches', 'git_main_name', 'git_origin_repo', 'git_local_repo',
           'git_last_commit', 'github_url', 'today']

# %% ../nbs/02_utils.ipynb 3
import io, json, sys, re, csv, logging
import git
from types import SimpleNamespace
from logging import Formatter
from logging.handlers import RotatingFileHandler
from fastcore.foundation import L
from datetime import datetime
from rich import box
from rich.table import Table
from rich.console import Console
from rich.logging import RichHandler
from fastcore.basics import ifnone, listify, store_attr
from fastcore.xtras import run
from pathlib import Path
from execnb.nbio import read_nb

# %% ../nbs/02_utils.ipynb 6
LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# %% ../nbs/02_utils.ipynb 7
LOGFORMAT_RICH = "%(message)s"

# %% ../nbs/02_utils.ipynb 8
def create_table(columns=["Notebook Path", "Status", "Run Time", "Colab"], xtra_cols=None) -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.box = box.SQUARE

    table.border_style = "bright_yellow"
    table.row_styles = ["none", "dim"]
    for col in columns + listify(xtra_cols):
        table.add_column(col)
    table.columns[1].style = "cyan"
    return table

# %% ../nbs/02_utils.ipynb 10
def remove_rich_format(text):
    "Remove rich fancy coloring"
    text = str(text)
    res = re.search(r"\](.*?)\[", text)
    if res is None:
        return text
    else:
        return res.group(1)

# %% ../nbs/02_utils.ipynb 12
def _csv_to_md(csv_file_path, delimiter=";"):
    
    
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
    return md_string

def csv_to_md(csv_file_path, delimiter=";"):
    "From csv file to markdown table, useful for github posting"
    md_string = _csv_to_md(csv_file_path, delimiter)
    output_file = Path(csv_file_path).with_suffix(".md")
    file = open(output_file, "w", encoding="UTF-8")
    file.write(md_string)
    file.close()

# %% ../nbs/02_utils.ipynb 15
STATUS = SimpleNamespace(
    ok="[green]Ok[/green]:heavy_check_mark:", fail="[red]Fail[/red]", skip="[green]Skipped[/green]:heavy_check_mark:"
)

# %% ../nbs/02_utils.ipynb 16
def _format_row(fname: Path, status: str, time: str, xtra_col=None, fname_only: bool = True) -> tuple:
    "Format one row for a rich.Table"

    formatted_status = getattr(STATUS, status.lower())
    fname = fname.name if fname_only else fname
    row = (str(fname), formatted_status, f"{int(time)}s")
    if len(listify(xtra_col)) > 0:
        row += (str(xtra_col),)
    return row

# %% ../nbs/02_utils.ipynb 18
class RichLogger:
    "A simple logger that logs to a file and the rich console"

    def __init__(self, columns, out_file="summary_table.csv", width=180):
        store_attr()
        self.data = []
        self.links = []
        self.console = Console(width=width, record=True)
        rh = RichHandler(console=self.console)
        rh.setFormatter(Formatter(LOGFORMAT_RICH))
        logging.basicConfig(
            level=logging.ERROR,
            format=LOGFORMAT,
            handlers=[
                rh,
                RotatingFileHandler("log.txt", maxBytes=1024 * 1024 * 10, backupCount=10),  # 10Mb
            ],
        )
        self.logger = logging.getLogger("rich")
        self.info(f"CONSOLE.is_terminal(): {self.console.is_terminal}")
        self.info(f"Writing output to {out_file}")

    def writerow(self, row, colab_link=None):
        self.data.append(row)
        self.links.append(colab_link)

    def writerow_incolor(self, fname, status, time, colab_link):
        "Same as write row, but color status"
        row = _format_row(fname, status, time)
        self.writerow(row, colab_link)

    def to_csv(self, out_file, delimiter=";", format_link=False):
        self.csv_file = open(out_file, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file, delimiter=delimiter)
        # write header
        self.csv_writer.writerow(self.columns)
        for row, link in zip(self.data, self.links):
            if format_link:
                fname = self._format_colab_link_md(link, row[0])
            else:
                fname = row[0]
            self.csv_writer.writerow([fname] + [remove_rich_format(e) for e in row[1:]])
        self.csv_file.close()

    def to_table(self, enum=True):
        columns = (["#"] + self.columns) if enum else self.columns
        table = create_table(columns=columns)
        for i, (row, link) in enumerate(zip(self.data, self.links)):
            fname = self._format_colab_link(link, row[0])
            table.add_row(f"{i}", fname, *row[1:])
        self.console.print(table)

    def to_md(self, out_file):
        csv_file = Path(out_file).with_suffix(".csv")
        self.to_csv(csv_file)
        csv_to_md(csv_file)
        self.info(f"Output table saved to [red]{out_file}[/red]")

    @property
    def info(self):
        return self.logger.info

    @property
    def warning(self):
        return self.logger.warning

    @property
    def exception(self):
        return self.logger.exception

    @property
    def error(self):
        return self.logger.error

    @staticmethod
    def _format_colab_link(colab_link, fname):
        return f"[link={colab_link}]{fname}[link]"

    @staticmethod
    def _format_colab_link_md(colab_link, fname):
        return f"[{fname}]({colab_link})"

# %% ../nbs/02_utils.ipynb 22
def is_nb(fname: Path):
    "filter files that are jupyter notebooks"
    return (fname.suffix == ".ipynb") and (not fname.name.startswith("_")) and (not "checkpoint" in str(fname))  and (not fname.is_symlink())

# %% ../nbs/02_utils.ipynb 24
def load_list_from_file(path: Path):
    "Load a list from a file"
    return path.read_text().split("\n")

def load_notebooks_from_file(path: Path):
    "Load a list of notebooks from a file"
    files = [Path(f) for f in load_list_from_file(path)]
    return [f.resolve() for f in files if is_nb(f)]

# %% ../nbs/02_utils.ipynb 26
def find_nbs(path: Path):
    "Get all nbs on path recursively"
    path = Path(path).resolve()
    if is_nb(path):
        return [path]
    if path.suffix == ".txt":
        return load_notebooks_from_file(path)
    return L([nb.resolve() for nb in path.rglob("*.ipynb") if is_nb(nb)]).sorted()

# %% ../nbs/02_utils.ipynb 31
def print_output(notebook):  # pragma: no cover
    "Print `notebook` in stdout for git things"
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    x = json.dumps(notebook, sort_keys=True, indent=1, ensure_ascii=False)
    output_stream.write(x)
    output_stream.write("\n")
    output_stream.flush()

# %% ../nbs/02_utils.ipynb 33
CellType = SimpleNamespace(code="code", md="markdown")

# %% ../nbs/02_utils.ipynb 34
def search_cell(cell, string) -> bool:
    "Search string in cell source, can be a list"
    source = listify(cell["source"])
    source = "".join(source)
    if string in source:
        return True
    return False

# %% ../nbs/02_utils.ipynb 37
def search_cells(nb, string: str = None, cell_type=CellType.code):
    "Get cells containing string, you can pass comma separated strings"
    strings = ifnone(string, "").replace(" ", "").split(",")
    cells = []
    for cell in nb["cells"]:
        if cell["cell_type"] == cell_type:
            if any([search_cell(cell, string) for string in strings]):
                cells.append(cell["source"])
    return cells

# %% ../nbs/02_utils.ipynb 41
def search_string_in_nb(nb, string: str = None, cell_type=CellType.code):
    "Check if string is present in notebook cells, you can pass comma separated strings"
    return len(search_cells(nb, string, cell_type)) > 0

# %% ../nbs/02_utils.ipynb 44
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
        if string:
            libs.append(string.replace(" ", "").split(","))
    return L(libs).concat().unique()

# %% ../nbs/02_utils.ipynb 48
def detect_imported_libs(notebook):
    "Guess imported libs from notebook"
    text_list = L(search_cells(notebook, "import,from")).concat()

    # format lines
    text_list = L([x.split("\n") for x in text_list]).concat()
    text_list = [line for line in text_list if (("from" in line) or ("import" in line))]

    return extract_libs(text_list)

# %% ../nbs/02_utils.ipynb 52
def get_repo(fname) -> git.Repo:
    try:
        repo = git.Repo(fname, search_parent_directories=True)
        return repo
    except Exception as e:
        raise Exception(f"Probably not in a git repo: {e}")

# %% ../nbs/02_utils.ipynb 54
def git_current_branch(fname) -> str:
    "Get current git branch"
    repo = get_repo(fname)
    try:
        return repo.active_branch.name
    except Exception as e:
        return "master"

# %% ../nbs/02_utils.ipynb 56
def git_branches(repo: git.Repo, remote=True):
    "Get all remote or local banches"
    branches = set([b.name for b in repo.branches])
    remote_branches =  set([r.name.split("/")[-1] for r in repo.remote().refs])
    return branches.union(remote_branches) if remote else branches

# %% ../nbs/02_utils.ipynb 58
def git_main_name(fname) -> str:
    "Get the name of master/main branch"
    repo = get_repo(fname)
    branches = git_branches(repo)
    return "main" if "main" in branches else "master"

# %% ../nbs/02_utils.ipynb 62
def _get_github_repo_remote(repo_url):
    if "git@" in repo_url:
        github_repo = re.search(r".com:(.*).git", repo_url).group(1)
    else:
        github_repo = re.search(r".com/(.*)", repo_url).group(1)
        if github_repo.endswith(".git"):
            github_repo = github_repo[:-4]
    return github_repo

# %% ../nbs/02_utils.ipynb 64
def git_origin_repo(fname):
    "Get github repo name from `fname`"
    repo = get_repo(fname)
    repo_url = repo.remote().url

    # check if ssh or html
    if repo_url != "":
        return _get_github_repo_remote(repo_url)
    else:
        raise Exception(f"Not in a valid github repo: {fname=}")

# %% ../nbs/02_utils.ipynb 66
def git_local_repo(fname):
    "Get local github repo path"
    repo = get_repo(fname)
    return Path(repo.git_dir).parent.resolve()

# %% ../nbs/02_utils.ipynb 68
def git_last_commit(fname):
    "Gets the last commit on fname"
    repo = get_repo(fname)
    return repo.commit().hexsha

# %% ../nbs/02_utils.ipynb 70
def github_url(fname, branch=None):
    "Get corresponding github URL"
    fname = fname.resolve()
    branch = ifnone(branch, git_main_name(fname))
    repo = git_origin_repo(fname)
    fname = fname.relative_to(git_local_repo(fname))
    return f"https://github.com/{repo}/blob/{branch}/{str(fname)}"

# %% ../nbs/02_utils.ipynb 73
def today():
    "datetime object containing current date and time"
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string
