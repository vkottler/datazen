"""
datazen - Top-level APIs for loading and interacting with configuration data.
"""

# built-in
from typing import List

# internal
from datazen.load import load_dir, LoadedFiles, DEFAULT_LOADS


def load(
    directories: List[str],
    variable_data: dict = None,
    loads: LoadedFiles = DEFAULT_LOADS,
) -> dict:
    """Load configuration data from a list of directories."""

    result: dict = {}
    for directory in directories:
        load_dir(directory, result, variable_data, loads)
    return result
