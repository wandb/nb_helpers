import json, io

## All this comes straight from fastai/nbdev

def rm_execution_count(o):
    "Remove execution count in `o`"
    if 'execution_count' in o: o['execution_count'] = None

colab_json = "application/vnd.google.colaboratory.intrinsic+json"
def clean_output_data_vnd(o):
    "Remove `application/vnd.google.colaboratory.intrinsic+json` in data entries"
    if 'data' in o:
        data = o['data']
        if colab_json in data:
            new_data = {k:v for k,v in data.items() if k != colab_json}
            o['data'] = new_data

def clean_cell_output(cell):
    "Remove execution count in `cell`"
    if 'outputs' in cell:
        for o in cell['outputs']:
            rm_execution_count(o)
            clean_output_data_vnd(o)
            o.get('metadata', o).pop('tags', None)

cell_metadata_keep = ["hide_input"]
nb_metadata_keep   = ["kernelspec", "jekyll", "jupytext", "doc"]

def clean_cell(cell, clear_all=False):
    "Clean `cell` by removing superfluous metadata or everything except the input if `clear_all`"
    rm_execution_count(cell)
    if 'outputs' in cell:
        if clear_all: cell['outputs'] = []
        else:         clean_cell_output(cell)
    if cell['source'] == ['']: cell['source'] = []
    cell['metadata'] = {} if clear_all else {k:v for k,v in cell['metadata'].items() if k in cell_metadata_keep}

def clean_nb(nb, clear_all=False):
    "Clean `nb` from superfluous metadata, passing `clear_all` to `clean_cell`"
    for c in nb['cells']: clean_cell(c, clear_all=clear_all)
    nb['metadata'] = {k:v for k,v in nb['metadata'].items() if k in nb_metadata_keep }