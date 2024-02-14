import importlib.machinery
import importlib.util
from pathlib import Path


def import_set_version():
    """Imports the set_version script as a python module and returns it."""
    loader = importlib.machinery.SourceFileLoader(
        'set_version',
        str(Path(__file__).parent.joinpath("..", "set_version"))
    )
    spec = importlib.util.spec_from_loader('set_version', loader)
    sv = importlib.util.module_from_spec(spec)
    loader.exec_module(sv)

    return sv
