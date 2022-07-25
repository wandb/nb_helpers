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

LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGFORMAT_RICH = "%(message)s"

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


STATUS = SimpleNamespace(
    ok="[green]Ok[/green]:heavy_check_mark:", fail="[red]Fail[/red]", skip="[green]Skipped[/green]:heavy_check_mark:"
)


def _format_row(fname: Path, status: str, time: str, xtra_col=None, fname_only: bool = True) -> tuple:
    "Format one row for a rich.Table"

    formatted_status = getattr(STATUS, status.lower())
    fname = fname.name if fname_only else fname
    row = (str(fname), formatted_status, f"{int(time)}s")
    if len(listify(xtra_col)) > 0:
        row += (str(xtra_col),)
    return row


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

    def create_github_issue(self, github_issue_file="github_issue.md", table=True, message=None):
        github_issue_file = Path(github_issue_file)
        with open(github_issue_file, "w", encoding="utf-8") as file:
            header = (
                f"# Summary: {today()}\n"
                "> This file was created automatically!\n\n"
                "To generate this table run:\n"
                "```bash\n$ nb_helpers.summary_nbs\n```\n"
            )
            file.write(header)
            if table:
                self.to_md("summary_table.md")
                table = open("summary_table.md", encoding="utf-8")
                file.write(table.read())
                table.close()
            if message is not None:
                file.write(message)
        self.info(f"Creating github issue via file: {github_issue_file}")


# nb
def is_nb(fname: Path):
    "filter files that are jupyter notebooks"
    return (fname.suffix == ".ipynb") and (not fname.name.startswith("_")) and (not "checkpoint" in str(fname))


def find_nbs(path: Path):
    "Get all nbs on path recursively"
    path = Path(path).resolve()
    if is_nb(path):
        return [path.resolve()]
    return L([nb.resolve() for nb in path.rglob("*.ipynb") if is_nb(nb)]).sorted()


def print_output(notebook):  # pragma: no cover
    "Print `notebook` in stdout for git things"
    output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    x = json.dumps(notebook, sort_keys=True, indent=1, ensure_ascii=False)
    output_stream.write(x)
    output_stream.write("\n")
    output_stream.flush()


CellType = SimpleNamespace(code="code", md="markdown")


def search_cell(cell, string) -> bool:
    "Search string in cell source, can be a list"
    source = listify(cell["source"])
    source = "".join(source)
    if string in source:
        return True
    return False


def search_cells(nb, string: str = None, cell_type=CellType.code):
    "Get cells containing string, you can pass comma separated strings"
    strings = ifnone(string, "").replace(" ", "").split(",")
    cells = []
    for cell in nb["cells"]:
        if cell["cell_type"] == cell_type:
            if any([search_cell(cell, string) for string in strings]):
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
        if string:
            libs.append(string.replace(" ", "").split(","))
    return L(libs).concat().unique()


def detect_imported_libs(notebook):
    "Guess imported libs from notebook"
    text_list = search_cells(notebook, "import,from")

    # format lines
    text_list = L([x.split("\n") for x in text_list]).concat()
    text_list = [line for line in text_list if (("from" in line) or ("import" in line))]

    return extract_libs(text_list)


## Git
def git_current_branch(fname) -> str:
    "Get current git branch"
    repo = git.Repo(fname, search_parent_directories=True)
    return repo.active_branch.name


def git_main_name(fname) -> str:
    "Get the name of master/main branch"
    try:
        repo = git.Repo(fname, search_parent_directories=True)
        branches = [b.name for b in repo.branches]
    except Exception as e:
        print(f"Probably not in a git repo: {e}")
        return "master"
    return "main" if "main" in branches else "master"


def git_origin_repo(fname):
    "Get github repo name from `fname`"
    try:
        repo = git.Repo(fname, search_parent_directories=True)
        repo_url = repo.remote().url

        # check if ssh or html
        if "git@" in repo_url:
            github_repo = re.search(r".com:(.*).git", repo_url).group(1)
        else:
            github_repo = re.search(r".com/(.*).git", repo_url).group(1)
        return github_repo

    except Exception as e:
        print(f"Probably not in a git repo: {e}")
        return ""


def git_local_repo(fname):
    "Get local github repo path"
    repo = git.Repo(fname, search_parent_directories=True)
    return Path(repo.git_dir).parent.resolve()


def git_last_commit(fname):
    "Gets the last commit on fname"
    repo = git.Repo(fname, search_parent_directories=True)
    return repo.commit().hexsha


# other stuff
def today():
    "datetime object containing current date and time"
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string
