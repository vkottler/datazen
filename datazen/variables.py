"""
datazen - Top-level APIs for loading and interacting with variables.
"""

# built-in
from typing import List

# internal
from datazen.load import load_dir, LoadedFiles, DEFAULT_LOADS


def load(
    directories: List[str],
    loads: LoadedFiles = DEFAULT_LOADS,
) -> dict:
    """Load variable data from a list of directories."""

    result: dict = {}
    for directory in directories:
        load_dir(directory, result, None, loads)
    return result
