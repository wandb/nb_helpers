import importlib
import os

from invoke import Collection  # pylint: disable=E0401

namespace = Collection()  # pylint: disable=C0103

INVOKE_DIRS = ['helpers']


for invoke_dir in INVOKE_DIRS:
    path_join = os.path.join(os.path.dirname(os.path.realpath(__file__)), invoke_dir)
    for filename in os.listdir(path_join):
        if filename.endswith('.py') and not filename.startswith('__'):
            modname = filename[:-3]
            mod = importlib.import_module('.' + modname, package=invoke_dir)
            namespace.add_collection(mod)