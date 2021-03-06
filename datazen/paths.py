
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

FMT_OPEN = "{"
FMT_CLOSE = "}"


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


def format_resolve_delims(value: str, fmt_data: dict, delim: str = ".",
                          delim_replace: str = "_") -> str:
    """
    Attempt to resolve a format String with data, but handle replacements with
    custom delimeters correctly.
    """

    open_len = value.count(FMT_OPEN)
    assert open_len == value.count(FMT_CLOSE)

    # if no parameters are specified, just return the provided String
    if open_len == 0:
        return value

    # replace "a.b.c" with "a_b_c", fmt_data should be a flat Dict[str, str]
    new_data: dict = {}
    for key, item in fmt_data.items():
        assert isinstance(key, str)
        new_data[key.replace(delim, delim_replace)] = item

    # re-build the format String
    fstr = ""
    tmp_value = value
    for _ in range(open_len):
        start = tmp_value.index(FMT_OPEN) + 1
        end = tmp_value.index(FMT_CLOSE)
        fstr += tmp_value[:start - 1]
        fstr += "{"
        fstr += tmp_value[start:end].replace(delim, delim_replace)
        tmp_value = tmp_value[end + 1:]
        fstr += "}"

    if len(fstr) < len(value):
        fstr += value[len(fstr):]

    return fstr.format(**new_data)


def unflatten_dict(data: dict, delim: str = ".") -> dict:
    """
    Attempt to unflatten dictionary data based on String keys and a delimeter.
    """

    result: dict = {}

    for key, value in data.items():
        # unflatten any dictionaries in the value
        if isinstance(value, dict):
            value = unflatten_dict(value)
        elif isinstance(value, list):
            new_value = []
            for item in value:
                if isinstance(item, dict):
                    item = unflatten_dict(item)
                new_value.append(item)
            value = new_value

        # move data["a.b.c"] = value to data["a"]["b"]["c"] = value
        if isinstance(key, str):
            to_advance = key.split(delim)
            to_update = advance_dict_by_path(to_advance[:-1], result)
            to_update[to_advance[-1]] = value
        else:
            result[key] = value

    return result


def advance_dict_by_path(path_list: List[str], data: dict) -> dict:
    """
    Given a dictionary and a list of directory names, return the child
    dictionary advanced by each key, in order, from the provided data.
    """

    for path in path_list:
        if path and isinstance(data, dict):
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
