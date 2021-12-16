from pathlib import Path

TEST_PATH = Path(__file__).parent
TEST_NB = TEST_PATH / "data/test_nb.ipynb"
FAIL_NB = TEST_PATH / "data/dummy_folder/fail_nb.ipynb"
SKIP_NB = TEST_PATH / "data/dummy_folder/test_nb_all_slow.ipynb"
FLAG_NB = TEST_PATH / "data/dummy_folder/test_nb_all_slow.ipynb"
