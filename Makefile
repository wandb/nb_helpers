.ONESHELL:
SHELL := /bin/bash

SRC = $(wildcard nbs/*.ipynb)

test:
	nb_helpers.run_nbs

release: pypi
	fastrelease_conda_package --mambabuild --upload_user wandb
	fastrelease_bump_version

conda_release:
	fastrelease_conda_package --mambabuild --upload_user wandb

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist

