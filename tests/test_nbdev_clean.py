import pytest
from fastcore.test import test_eq as meta_assert_eq
from nb_helpers.nbdev_clean import clean_cell, clean_nb

## from nbdev.clean


@pytest.fixture
def colab_cell():
    tst = {
        "cell_type": "code",
        "execution_count": 26,
        "metadata": {"hide_input": True, "meta": 23},
        "outputs": [
            {
                "execution_count": 2,
                "data": {
                    "application/vnd.google.colaboratory.intrinsic+json": {
                        "type": "string"
                    },
                    "plain/text": [
                        "sample output",
                    ],
                },
                "output": "super",
            }
        ],
        "source": "awesome_code",
    }
    return tst


def test_clean_colab_cell(colab_cell):
    "Test cleaning one cell of jupyter from metadata and outputs"

    clean_cell(colab_cell)
    meta_assert_eq(
        colab_cell,
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {"hide_input": True},
            "outputs": [
                {
                    "execution_count": None,
                    "data": {
                        "plain/text": [
                            "sample output",
                        ]
                    },
                    "output": "super",
                }
            ],
            "source": "awesome_code",
        },
    )

    clean_cell(colab_cell, clear_all=True)
    meta_assert_eq(
        colab_cell,
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": "awesome_code",
        },
    )


def test_clean_mkdown_cell(colab_cell):
    "Test cleaning one mkdown cell"

    mkdown_cell = {
        "metadata": {"tags": []},
        "outputs": [{"metadata": {"tags": []}}],
        "source": [""],
    }
    clean_cell(mkdown_cell, clear_all=False)
    meta_assert_eq(
        mkdown_cell, {"metadata": {}, "outputs": [{"metadata": {}}], "source": []}
    )


def test_clean_nb(colab_cell):
    "Clean whole notebook"
    nb = {
        "metadata": {"kernelspec": "some_spec", "jekyll": "some_meta", "meta": 37},
        "cells": [colab_cell],
    }

    clean_nb(nb)
    meta_assert_eq(
        nb["cells"][0],
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {"hide_input": True},
            "outputs": [
                {
                    "execution_count": None,
                    "data": {
                        "plain/text": [
                            "sample output",
                        ]
                    },
                    "output": "super",
                }
            ],
            "source": "awesome_code",
        },
    )
    meta_assert_eq(nb["metadata"], {"kernelspec": "some_spec", "jekyll": "some_meta"})
