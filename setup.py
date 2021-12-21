import setuptools


lib_name = "nb_helpers"
min_python = "3.7"

setuptools.setup(
    name="nb_helpers",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["rich", "fastcore", "fastprogress", "nbdev"],
    python_requires=">=" + "3.7",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "clean_nbs=nb_helpers.clean:clean_nbs",
            "run_nbs=nb_helpers.run:run_nbs",
            "summary_nbs=nb_helpers.wandb:summary_nbs",
        ]
    },
)
