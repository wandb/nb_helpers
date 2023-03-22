from pathlib import Path

from nb_helpers.actions import upload_modified_nbs

upload_modified_nbs("tcapelle", "nb_helpers", pr_message=Path.cwd()/"pr_message.md")