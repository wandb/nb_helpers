from ast import Param
import glob
import time
from pathlib import Path
from fastcore.script import *

import nbformat
from fastcore.basics import num_cpus
from nbconvert.preprocessors import ExecutePreprocessor

from nb_helpers.utils import find_nbs


def read_nb(fname):
    "Read the notebook in `fname`."
    with open(Path(fname), "r", encoding="utf8") as f:
        return nbformat.reads(f.read(), as_version=4)


def run_one(fname, verbose=True):
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

@call_parse
def test_nbs(
    path:    Param("A notebook name or glob to convert", str) = '.', 
    verbose: Param("Print errors along the way", store_true) = False, 
    timing:  Param("Timing each notebook to see the ones are slow", store_true) = False,
):
    files = find_nbs(Path(path))
    results = []
    for nb in files:
        results.append(run_one(nb, verbose=verbose))
        time.sleep(0.5)
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
