
"""
datazen - APIs for working with file paths.
"""

# built-in
import os
import pkgutil
from typing import List

# third-party
import pkg_resources

# internal
from datazen import PKG_NAME


def get_file_name(full_path: str) -> str:
    """ From a full path to a file, get just the name of the file. """

    return ".".join(os.path.basename(full_path).split(".")[:-1])


def get_file_ext(full_path: str) -> str:
    """ From a pull path to a file, get just the file's extension. """

    return os.path.basename(full_path).split(".")[-1]


def get_path_list(root_abs_path: str, current_abs_path: str) -> List[str]:
    """
    From a root directory and a child path, compute the list of directories,
    in order, mapping the root to the child.
    """

    assert len(current_abs_path) >= len(root_abs_path)
    assert root_abs_path in current_abs_path
    return current_abs_path[len(root_abs_path):].split(os.sep)


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


def get_package_data(relative_path: str) -> str:
    """ Load a file from this package's data directory. """

    rel_path = os.path.join("data", relative_path)
    schema_raw = pkgutil.get_data(PKG_NAME, rel_path)
    schema_bytes = schema_raw if schema_raw else bytes()
    return schema_bytes.decode("utf-8")


def get_package_dir(relative_path: str) -> str:
    """ Locate the path to a package-data directory. """

    return pkg_resources.resource_filename(__name__,
                                           os.path.join("data", relative_path))


def resolve_dir(data: str, rel_base: str = "") -> str:
    """
    Turn directory data into an absolute path, optionally from a relative
    base.
    """

    data = data.replace("/", os.sep)
    data = data.replace("\\", os.sep)
    if not os.path.isabs(data) and rel_base:
        data = os.path.join(rel_base, data)
    return os.path.abspath(data)
