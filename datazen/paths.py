
"""
datazen - APIs for working with file paths.
"""

# built-in
import os
from typing import List


def get_file_name(full_path: str) -> str:
    """ From a full path to a file, get just the name of the file. """

    return os.path.basename(full_path).split(".")[0]


def get_file_ext(full_path: str) -> str:
    """ From a pull path to a file, get just the file's extension. """

    return os.path.basename(full_path).split(".")[1]


def get_path_list(root_abs_path: str, current_abs_path: str) -> List[str]:
    """
    From a root directory and a child path, compute the list of directories,
    in order, mapping the root to the child.
    """

    assert len(current_abs_path) >= len(root_abs_path)

    index = 0
    for char in enumerate(root_abs_path):
        if char[1] != current_abs_path[char[0]]:
            break
        index = index + 1
    assert index > 0

    return current_abs_path[index:].split(os.sep)


def advance_dict_by_path(path_list: List[str], data: dict) -> dict:
    """
    Given a dictionary and a list of directory names, return the child
    dictionary advanced by each key, in order, from the provided data.
    """

    for path in path_list:
        if path:
            try:
                data = data[path]
            except KeyError:
                data[path] = {}
                data = data[path]

    return data
