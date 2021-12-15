from pathlib import Path
from tests import TEST_PATH, TEST_NB
from nb_helpers.utils import is_nb, find_nbs, git_current_branch, git_origin_repo, read_nb, search_string_in_nb



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


# nb
def test_search_string_in_nb():
    nb = read_nb(TEST_NB)
    assert search_string_in_nb(nb, "writer") is True, "We open and write a file"
    assert search_string_in_nb(nb, "pandas") is False, "pandas is not used in this notebook"

# git
def test_git_current_branch():
    assert git_current_branch() == 'main', "Maybe you are not in main?"

def test_git_origin_repo():
    assert git_origin_repo() == 'github/wandb/nb_helpers/blob/main', "Maybe not in main? not in nb_helpers?"
