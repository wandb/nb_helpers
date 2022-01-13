![CI](https://github.com/wandb/nb_helpers/workflows/CI/badge.svg)

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
- Summary:
You can get a summary of the notebooks in your project with the `nb_helpers.summary_nbs` function.

```
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