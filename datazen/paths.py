
"""
datazen - APIs for working with file paths.
"""

# built-in
import os
from typing import List


def get_path_list(root_abs_path: str, current_abs_path: str) -> List[str]:
    """ TODO """

    assert len(current_abs_path) >= len(root_abs_path)

    index = 0
    for char in enumerate(root_abs_path):
        if char[1] != current_abs_path[char[0]]:
            break
        index = index + 1
    assert index > 0

    return current_abs_path[index:].split(os.sep)


def advance_dict_by_path(path_list: List[str], data: dict) -> dict:
    """ TODO """

    for path in path_list:
        if path:
            try:
                data = data[path]
            except KeyError:
                data[path] = {}
                data = data[path]

    return data
