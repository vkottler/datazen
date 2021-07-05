"""
datazen - Top-level APIs for loading and interacting with variables.
"""

# built-in
from typing import List, Dict

# internal
from datazen.load import load_dir


def load(
    directories: List[str],
    loaded_list: List[str] = None,
    hashes: Dict[str, dict] = None,
) -> dict:
    """Load variable data from a list of directories."""

    result: dict = {}
    for directory in directories:
        load_dir(directory, result, None, loaded_list, hashes)
    return result
