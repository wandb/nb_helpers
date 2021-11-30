![CI](https://github.com/wandb/nb_helpers/workflows/CI/badge.svg)

# nb_helpers

A simple tool to clean up notebooks from your repo

## Install
Clone and then install using git:
```bash
pip install .
```

## Usage

This little library gives you command line tools to clean, test and check your jupyter notebooks.

- Clean: When you call `clean_nbs` it will strip notebooks from the metadata, this helps prevent git conflicts. You can also pass the flag `--clear_outs` and also remove cell outputs.
```bash
clean_nbs
> 
┏━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Notebook Path ┃ Status ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ test_nb.ipynb │ Ok     │
└───────────────┴────────┘
```

## Usage on CI/CD of other projects

The main idea of this repo, is to strip out notebooks from `wandb/examples`. 

- TODO: test notebooks, as this cannot be done on github runners.