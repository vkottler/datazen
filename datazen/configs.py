"""
datazen - Top-level APIs for loading and interacting with configuration data.
"""

# built-in
from typing import Dict, List

# internal
from datazen.load import load_dir


def load(
    directories: List[str],
    variable_data: dict = None,
    loaded_list: List[str] = None,
    hashes: Dict[str, dict] = None,
) -> dict:
    """Load configuration data from a list of directories."""

    result: dict = {}
    for directory in directories:
        load_dir(directory, result, variable_data, loaded_list, hashes)
    return result
