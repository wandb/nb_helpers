![CI](https://github.com/wandb/nb_helpers/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/wandb/nb_helpers/branch/main/graph/badge.svg?token=2W6CRFZ7CB)](https://codecov.io/gh/wandb/nb_helpers)

# nb_helpers

A simple tool to clean, test and fix notebooks for your repo

## Install
You can install from pypi:
```bash
pip install nb_helpers
```
or get latest:
```bash
pip install -e .
```

## Usage

This little library gives you command line tools to clean, test and check your jupyter notebooks.

- Clean: When you call `clean_nbs` it will strip notebooks from the metadata, this helps prevent git conflicts. You can also pass the flag `--clear_outs` and also remove cell outputs.
```bash
$ nb_helpers.clean_nbs --help                                                                                                                                   tcapelle at MBP14.local (-)(main)
usage: nb_helpers.clean_nbs [-h] [--path PATH] [--clear_outs] [--verbose]

Clean notebooks on `path` from useless metadata

options:
  -h, --help    show this help message and exit
  --path PATH   The path to notebooks (default: .)
  --clear_outs  Remove cell outputs (default: False)
  --verbose     Rnun on verbose mdoe (default: False)
```

You can run this comman on this repo:

```bash
$ nb_helpers.clean_nbs
> 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓                                                                     
┃ Notebook Path                                   ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ tests/data/dummy_folder/fail_nb.ipynb           │ Ok✔    │
│ tests/data/dummy_folder/test_nb2.ipynb          │ Ok✔    │
│ tests/data/dummy_folder/test_nb_all_slow.ipynb  │ Ok✔    │
│ tests/data/dummy_folder/test_nb_some_slow.ipynb │ Ok✔    │
│ tests/data/features_nb.ipynb                    │ Ok✔    │
│ tests/data/test_nb.ipynb                        │ Ok✔    │
└─────────────────────────────────────────────────┴────────┘
```
- Run: One can run the notebooks in `path` and get info about the execution.
```bash
$ nb_helpers.run_nbs --help                                                                                                                                     tcapelle at MBP14.local (-)(main)
usage: nb_helpers.run_nbs [-h] [--path PATH] [--verbose] [--flags FLAGS] [--timeout TIMEOUT] [--lib_name LIB_NAME] [--no_run] [--post_issue]

options:
  -h, --help           show this help message and exit
  --path PATH          A path to nb files (default: .)
  --verbose            Print errors along the way (default: False)
  --flags FLAGS        Space separated list of flags
  --timeout TIMEOUT    Max runtime for each notebook, in seconds (default: 600)
  --lib_name LIB_NAME  Python lib names to filter, eg: tensorflow
  --no_run             Do not run any notebook (default: False)
  --post_issue         Post the failure in github (default: False)
```
You get the following output inside this repo:
```bash
$ nb_helpers.run_nbs
CONSOLE.is_terminal(): True
Writing output to run.csv
```
 | Notebook Path |Status |Run Time |colab |
 |--- | --- | --- | --- | 
 | dev_nbs/search.ipynb | Fail | 1 s | [open](https://colab.research.google.com/github/wandb/nb_helpers/blob/main/dev_nbs/search.ipynb) | 
 | tests/data/dummy_folder/fail_nb.ipynb | Fail | 1 s | [open](https://colab.research.google.com/github/wandb/nb_helpers/blob/main/tests/data/dummy_folder/fail_nb.ipynb) | 
 | tests/data/dummy_folder/test_nb2.ipynb | Ok | 0 s | [open](https://colab.research.google.com/github/wandb/nb_helpers/blob/main/tests/data/dummy_folder/test_nb2.ipynb) | 
 | tests/data/dummy_folder/test_nb_all_slow.ipynb | Skipped | 0 s | [open](https://colab.research.google.com/github/wandb/nb_helpers/blob/main/tests/data/dummy_folder/test_nb_all_slow.ipynb) | 
 | tests/data/dummy_folder/test_nb_some_slow.ipynb | Ok | 0 s | [open](https://colab.research.google.com/github/wandb/nb_helpers/blob/main/tests/data/dummy_folder/test_nb_some_slow.ipynb) | 
 | tests/data/features_nb.ipynb | Ok | 0 s | [open](https://colab.research.google.com/github/wandb/nb_helpers/blob/main/tests/data/features_nb.ipynb) | 
 | tests/data/test_nb.ipynb | Ok | 0 s | [open](https://colab.research.google.com/github/wandb/nb_helpers/blob/main/tests/data/test_nb.ipynb) | 
- Summary:
You can get a summary of the notebooks in your project with the `nb_helpers.summary_nbs` function.

```bash
$ nb_helpers.summary_nbs
CONSOLE.is_terminal(): True
Writing output to /Users/tcapelle/wandb/nb_helpers/logs/summary.csv
Reading 6 notebooks
┌───┬─────────────────────────────────────────────────┬────────────┬────────────────┬────────────────────────────────────────────────┬────────────┬───────┐
│ # │ nb name                                         │ tracker    │ wandb features │ python libs                                    │ colab_cell │ colab │
├───┼─────────────────────────────────────────────────┼────────────┼────────────────┼────────────────────────────────────────────────┼────────────┼───────┤
│ 1 │ tests/data/dummy_folder/fail_nb.ipynb           │            │                │                                                │            │ open  │
│ 2 │ tests/data/dummy_folder/test_nb2.ipynb          │            │                │                                                │            │ open  │
│ 3 │ tests/data/dummy_folder/test_nb_all_slow.ipynb  │            │                │ time                                           │            │ open  │
│ 4 │ tests/data/dummy_folder/test_nb_some_slow.ipynb │            │                │ time                                           │            │ open  │
│ 5 │ tests/data/features_nb.ipynb                    │            │                │ typing, itertools                              │            │ open  │
│ 6 │ tests/data/test_nb.ipynb                        │ 0: tracker │                │ os, sys, logging, pathlib, fastcore, itertools │ 1          │ open  │
└───┴─────────────────────────────────────────────────┴────────────┴────────────────┴────────────────────────────────────────────────┴────────────┴───────┘
```
------------
## Python Lib

All this functions can also be used inside python:
```python
from pathlib import Path
from nb_helpers.run import run_nbs

examples_path = Path("examples/colabs")

errors = run_nbs(path=examples_path, verbose=True, timeout=600)
```
Also the library has many little functions to make your life easier inside the repo you are orchestrating:
```python
from pathlib import Path
from nb_helpers.utils import *
from nb_helpers.colab import *

examples_path = Path("examples/colabs")

# get all nbs in the folder recursevely, filters hidden, non nb stuff
nb_files = find_nbs(example_path)

one_nb_path = nb_files[0]
notebook = read_nb(one_nb_path)

# get all libs imported
libs = detect_imported_libs(notebook)

# get remote github repo
github_repo = git_origin_repo(one_nb_path)

# detect if master is called main or master
master_name = git_main_name(one_nb_path)

# get colab link
colab_url = get_colab_url(one_nb_path, branch=master_name) 
```