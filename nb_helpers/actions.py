from fastcore.all import *
from ghapi.all import *

from nb_helpers.utils import is_nb
from nb_helpers.colab import get_colab_url

def get_colab_url2md(fname: Path, branch="main") -> str:
    "Create colab links in md"
    colab_url = get_colab_url(fname, branch)
    return f"[{colab_url.split(branch)[1]}]({colab_url})"

def create_comment_body(nb_files) -> str:
    "Creates a MD list of fnames with links to colab"
    title = "The following colabs where changed:"
    colab_links = tuple(get_colab_url2md(f) for f in nb_files)
    body = tuplify(title) + colab_links
    return "\n -".join(body)

def after_pr_colab_link(owner="wandb", repo="nb_helpers", token=None):
    "On PR post a comment with links to open in colab for each changed nb"

    api = GhApi(owner=owner, repo=repo, token=ifnone(token, github_token()))
    payload = context_github.event

    if "workflow" in payload:
        issue = 1
    else:
        if payload.action != "opened":
            return
        issue = payload.number

    pr = api.pulls.get(issue)
    github_repo, branch = pr.head.repo.full_name, pr.head.ref

    pr_files = [Path(f.filename) for f in api.pulls.list_files(issue)]

    # filter nbs
    nb_files = [f for f in pr_files if is_nb(f)]

    if len(nb_files) > 0:
        body = create_comment_body(nb_files)
        print(f">> Creating comment on PR #{issue}")
        api.issues.create_comment(issue_number=issue, body=body)
