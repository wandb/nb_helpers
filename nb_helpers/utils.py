import io, json, sys, re
from IPython import get_ipython
from fastcore.basics import ifnone
from fastcore.xtras import run
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


def uses_lib(nb, lib_name=None):
    "Chek if notebooks uses library `lib_name`"
    lib_name = ifnone(lib_name, "")
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            if lib_name in cell["source"]:
                return True
    return False


## colab
def is_colab():
    if 'google.colab' in str(get_ipython()):
        return True
    return False

## Git

def git_current_branch():
    "Get current git branch"
    return run('git branch --show-current')

def git_origin_repo():
    "Get git repo url, to append to colab"
    repo_url = run('git config --get remote.origin.url')
    if 'git@' in repo_url:
        github_repo = re.search(r":(.*?).git", repo_url).group(1)
        return f'github/{github_repo}/blob/{git_current_branch()}'
    else:
        return f'{repo_url}/blob/{git_current_branch()}'