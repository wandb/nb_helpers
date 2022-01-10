from pathlib import Path

from nbformat import read
from tests import TEST_PATH, TEST_NB, FAIL_NB
from nb_helpers.utils import is_nb, find_nbs, git_origin_repo, read_nb, search_string_in_nb
from nb_helpers.colab import in_colab, _has_colab_badge, add_colab_badge


def test_is_nb():
    bad_names = [
        Path("folder/.ipynb_checkpoints"),
        Path("folder/_file.ipynb"),
        Path("folder/checkpoint_file.ipynb"),
    ]
    assert not all([is_nb(f) for f in bad_names])


def test_find_nbs():
    valid_nbs = [f.name for f in find_nbs(TEST_PATH)]
    assert len(valid_nbs) == 6
    assert ("test_nb.ipynb" in valid_nbs) and ("test_nb2.ipynb" in valid_nbs)


# colab
def test_colab():
    assert not in_colab(), f"We are not in colab"


# nb
def test_search_string_in_nb():
    nb = read_nb(TEST_NB)
    assert search_string_in_nb(nb, "writer") is True, "We open and write a file"
    assert search_string_in_nb(nb, "pandas") is False, "pandas is not used in this notebook"


# git
def test_git_origin_repo():
    repo = git_origin_repo(TEST_NB)
    assert repo == f"wandb/nb_helpers", f"Maybe not a git repo? {repo}"


def test_colab_badge():
    nb = read_nb(TEST_NB)
    idx = _has_colab_badge(nb)
    assert idx == 1
    badged_nb = add_colab_badge(TEST_NB)
    idx = _has_colab_badge(badged_nb)
    assert idx == 0
    badged_nb = add_colab_badge(FAIL_NB)
    idx = _has_colab_badge(badged_nb)
    assert idx == 0
