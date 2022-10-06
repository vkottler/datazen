"""
datazen - Top-level APIs for loading and interacting with configuration data.
"""

# built-in
from typing import Iterable

# third-party
from vcorelib.dict import GenericStrDict
from vcorelib.io.types import LoadResult
from vcorelib.paths import Pathlike

# internal
from datazen.load import DEFAULT_LOADS, LoadedFiles, load_dir


def load(
    directories: Iterable[Pathlike],
    variable_data: GenericStrDict = None,
    loads: LoadedFiles = DEFAULT_LOADS,
) -> LoadResult:
    """Load configuration data from a list of directories."""

    result: GenericStrDict = {}
    errors = 0
    for directory in directories:
        errors += int(not load_dir(directory, result, variable_data, loads)[1])
    return LoadResult(result, errors == 0)
