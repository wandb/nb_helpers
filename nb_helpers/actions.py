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
        issue = payload.number
    pr = payload.pull_request
    github_repo = pr.head.repo.full_name
    branch = pr.head.ref
    pr_files = [Path(f.filename) for f in api.pulls.list_files(issue)]
    print(f'pr_files: {pr_files}')

    # filter nbs
    nb_files = [f for f in pr_files if is_nb(f)]

    def _get_comment_id(issue):
        comments = api.issues.list_comments(issue)
        candidates =  [c for c in comments if "The following colabs where changed in this PR" in c.body]
        if len(candidates)==1:
            comment_id = candidates[0].id
        else:
            comment_id = -1
        return comment_id

    if len(nb_files) > 0:
        body = create_comment_body(nb_files)
        comment_id = _get_comment_id(issue)
        if comment_id>0:
            print(f">> Updating comment on PR #{issue}\n{body}\n")
            api.issues.update_comment(comment_id, body)
        else:
            print(f">> Creating comment on PR #{issue}\n{body}\n")
            api.issues.create_comment(issue_number=issue, body=body)
