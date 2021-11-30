import glob
import time
from pathlib import Path

import nbformat
from fastcore.basics import num_cpus
from nbconvert.preprocessors import ExecutePreprocessor


def is_nb(fname):
    "filter files that are notebooks"
    return (
        (fname.suffix == ".ipynb")
        and (not fname.name.startswith("_"))
        and (not "checkpoint" in str(fname))
    )


TEST_NBS = [f for f in list(TEST_PATH.glob("**/*.ipynb")) if is_nb(f)]


def read_nb(fname):
    "Read the notebook in `fname`."
    with open(Path(fname), "r", encoding="utf8") as f:
        return nbformat.reads(f.read(), as_version=4)


def test_one(fname, verbose=True):
    "Run nb `fname` and timeit, recover exception"
    print(f"testing {fname}")
    start = time.time()
    try:
        notebook = read_nb(fname)
        processor = ExecutePreprocessor(timeout=600, kernel_name="python3")
        pnb = nbformat.from_dict(notebook)
        processor.preprocess(pnb)
        return True, time.time() - start
    except Exception as e:
        if verbose:
            print(f"\nError in executing {fname}\n{e}")
        return False, time.time() - start


def test(fname=None, n_workers=None, verbose=True, timing=False, pause=0.5):
    """Test in parallel the notebooks matching `fname`
    fname: "A notebook name or glob to convert" = None,
    n_workers: "Number of workers to use" = None,
    verbose: "Print errors along the way" = True,
    timing: "Timing each notebook to see the ones are slow" = False,
    pause: "Pause time (in secs) between notebooks to avoid race conditions" = 0.5,"""
    if fname is None:
        files = TEST_NBS
    else:
        files = glob.glob(fname)
    files = [Path(f).absolute() for f in sorted(files)]
    if n_workers is None:
        n_workers = 0 if len(files) == 1 else min(num_cpus(), 8)
    for nb in files:
        test_one(nb, verbose=verbose)
        time.sleep(pause)
    passed, times = [r[0] for r in results], [r[1] for r in results]
    if all(passed):
        print("All tests are passing!")
    else:
        msg = "The following notebooks failed:\n"
        raise Exception(
            msg + "\n".join([f.name for p, f in zip(passed, files) if not p])
        )
    if timing:
        for i, t in sorted(enumerate(times), key=lambda o: o[1], reverse=True):
            print(f"Notebook {files[i].name} took {int(t)} seconds")
