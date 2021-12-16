from pathlib import Path
from nb_helpers.clean import clean_all, clean_one
from tests import TEST_PATH

TEST_PATH
TEST_NB = Path("test_nb.py")


def test_clean_one():
    "clean just one nb"
    clean_one(TEST_NB)


def test_clean_all():
    "clean all test nbs"
    clean_all(path=TEST_PATH)
