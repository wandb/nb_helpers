from fastcore.all import *
from ghapi.all import *

def reply_thanks():
    api = GhApi(owner='wandb', repo='nb_helpers', token=github_token())
    payload = context_github.event
    if 'workflow' in payload: issue = 1
    else:
        if payload.action != 'opened': return
        issue = payload.number
    api.issues.create_comment(issue_number=issue, body='Thank you for your *valuable* contribution')

reply_thanks()