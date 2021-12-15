#######################################
# All this code comes from fastai/nbdev
#######################################

from nbconvert.preprocessors import ExecutePreprocessor
from nbdev.export import _mk_flag_re

TEST_FLAGS = "slow"


class _ReTstFlags:  # pragma: no cover
    "Test flag matching regular expressions"

    def __init__(self, all_flag):
        "match flags applied to all cells?"
        self.all_flag = all_flag

    def _deferred_init(self):
        "Compile at first use but not before since patterns need `get_config().tst_flags`"
        if hasattr(self, "_re"):
            return
        tst_flags = TEST_FLAGS
        tst_flags += f"|skip" if tst_flags else "skip"
        _re_all = "all_" if self.all_flag else ""
        self._re = _mk_flag_re(f"{_re_all}({tst_flags})", 0, "Any line with a test flag")

    def findall(self, source):
        self._deferred_init()
        return self._re.findall(source)

    def search(self, source):
        self._deferred_init()
        return self._re.search(source)


_re_all_flag = _ReTstFlags(True)


def get_all_flags(cells):
    "Check for all test flags in `cells`"
    result = []
    for cell in cells:
        if cell["cell_type"] == "code":
            result.extend(_re_all_flag.findall(cell["source"]))
    return set(result)


_re_flags = _ReTstFlags(False)


def get_cell_flags(cell):
    "Check for any special test flag in `cell`"
    if cell["cell_type"] != "code" or len(TEST_FLAGS) == 0:
        return []
    return _re_flags.findall(cell["source"])


class NoExportPreprocessor(ExecutePreprocessor):
    "An `ExecutePreprocessor` that executes cells that don't have a flag in `flags`"

    def __init__(self, flags, **kwargs):
        self.flags = flags
        super().__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        if "source" not in cell or cell["cell_type"] != "code":
            return cell, resources
        for f in get_cell_flags(cell):
            if f not in self.flags:
                return cell, resources
        # if check_re(cell, _re_notebook2script): return cell, resources
        return super().preprocess_cell(cell, resources, index)
