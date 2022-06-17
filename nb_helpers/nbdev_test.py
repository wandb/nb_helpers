#######################################
# All this code comes from fastai/nbdev
#######################################

from nbconvert.preprocessors import ExecutePreprocessor


class NoExportPreprocessor(ExecutePreprocessor):
    def __init__(self, pip_install=True, **kwargs):
        self.pip_install = pip_install
        super().__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        if "source" not in cell or cell["cell_type"] != "code":
            return cell, resources
        cell_source = "".join(cell["source"])
        if "pip" in cell_source and not self.pip_install:
            code = cell["source"]
            print(f"Skipping: {code}")
            return cell, resources
        return super().preprocess_cell(cell, resources, index)
