from pathlib import Path
from nb_helpers.clean import clean_one

TEST_NB = Path("test_nb.py")


def test_clean_one():
    clean_one(TEST_NB)
