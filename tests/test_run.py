from tests import TEST_NB, FAIL_NB, SKIP_NB, FLAG_NB, TEST_PATH
from nb_helpers.run import run_one


def test_run_one():
    # run and pass
    row, no_errors = run_one(TEST_NB)
    assert no_errors is None, f"Notebook {TEST_NB} failed"
    assert row[1] == "ok", f"Error, the notebooks produces {row[1]}!=ok"

    # run and fail
    row, errors = run_one(FAIL_NB)
    assert errors is not None, f"Notebook {FAIL_NB} has no errors, it should!"
    assert row[1] == "fail", f"Error, the notebooks produces {row[1]}!=fail"

    # # skipped
    # row, no_errors = run_one(SKIP_NB)
    # assert no_errors is None, f"Notebook {TEST_NB} failed"
    # assert row[1] == STATUS.skip, f"Error, the notebooks produces {row[1]}!=skip"

    # skipped cause pandas is not used in the nb
    row, _ = run_one(TEST_NB, lib_name="pandas")
    assert row[1] == "skip", f"Error, the notebooks produces {row[1]}!=skip"

    # run cause pathlib is there
    row, _ = run_one(TEST_NB, lib_name="pathlib")
    assert row[1] == "ok", f"Error, the notebooks produces {row[1]}!=ok"

    # # should not run cause it's flagged as slow
    # row, _ = run_one(FLAG_NB)
    # assert row[1] == STATUS.skip, f"Error, the notebooks produces {row[1]}!=skip"

    # # should run cause it's flagged as slow
    # row, _ = run_one(FLAG_NB, flags="slow")
    # assert row[1] == STATUS.ok, f"Error, the notebooks produces {row[1]}!=ok"
