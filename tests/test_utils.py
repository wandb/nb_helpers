from pathlib import Path
from tests import TEST_PATH
from nb_helpers.utils import is_nb, find_nbs


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
