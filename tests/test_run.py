from tests import TEST_NB, FAIL_NB, SKIP_NB, FLAG_NB, TEST_PATH
from nb_helpers.run import run_one


def test_run_one():
    # run and pass
    status, _ = run_one(TEST_NB)
    assert status == "ok", f"Error, the notebooks produces {status}!=ok"

    # run and fail
    status, _ = run_one(FAIL_NB)
    assert status == "fail", f"Error, the notebooks produces {status}!=fail"

    # skipped cause pandas is not used in the nb
    status, _ = run_one(TEST_NB, lib_name="pandas")
    assert status == "skip", f"Error, the notebooks produces {status}!=skip"

    # run cause pathlib is there
    status, _ = run_one(TEST_NB, lib_name="pathlib")
    assert status == "ok", f"Error, the notebooks produces {status}!=ok"
