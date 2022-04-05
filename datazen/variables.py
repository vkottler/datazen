"""
datazen - Top-level APIs for loading and interacting with variables.
"""

# built-in
from typing import List

# internal
from datazen.code.types import LoadResult
from datazen.load import DEFAULT_LOADS, LoadedFiles, load_dir


def load(
    directories: List[str],
    loads: LoadedFiles = DEFAULT_LOADS,
) -> LoadResult:
    """Load variable data from a list of directories."""

    result: dict = {}
    errors = 0
    for directory in directories:
        errors += int(not load_dir(directory, result, None, loads)[1])
    return LoadResult(result, errors == 0)
