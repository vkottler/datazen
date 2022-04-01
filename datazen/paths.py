"""
datazen - APIs for working with file paths.
"""

# built-in
import os
from pathlib import Path
import pkgutil
from typing import Iterator, List, Tuple, Union

# third-party
import pkg_resources

# internal
from datazen import PKG_NAME

FMT_OPEN = "{"
FMT_CLOSE = "}"
EXCLUDES = [".git", ".svn", ".gitignore"]


def get_file_name(path: Union[Path, str], **kwargs) -> str:
    """From a full path to a file, get just the name of the file."""

    return ".".join(os.path.basename(str(path)).split(".", **kwargs)[:-1])


def get_file_ext(path: Union[Path, str], **kwargs) -> str:
    """From a pull path to a file, get just the file's extension."""

    return os.path.basename(str(path)).split(".", **kwargs)[-1]


def get_path_list(
    root: Union[Path, str], current: Union[Path, str]
) -> List[str]:
    """
    From a root directory and a child path, compute the list of directories,
    in order, mapping the root to the child.
    """
    root = os.path.abspath(str(root))
    current = os.path.abspath(str(current))
    assert len(current) >= len(root)
    assert root in current
    return current[len(root) :].split(os.sep)


def format_resolve_delims(
    value: str, fmt_data: dict, delim: str = ".", delim_replace: str = "_"
) -> str:
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
        fstr += tmp_value[: start - 1]
        fstr += "{"
        fstr += tmp_value[start:end].replace(delim, delim_replace)
        tmp_value = tmp_value[end + 1 :]
        fstr += "}"

    if len(fstr) < len(value):
        fstr += value[len(fstr) :]

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


def get_package_data(relative: Union[Path, str]) -> str:
    """Load a file from this package's data directory."""

    rel_path = os.path.join("data", str(relative))
    schema_raw = pkgutil.get_data(PKG_NAME, rel_path)
    schema_bytes = schema_raw if schema_raw else bytes()
    return schema_bytes.decode("utf-8")


def get_package_dir(relative: Union[Path, str]) -> str:
    """Locate the path to a package-data directory."""

    return pkg_resources.resource_filename(
        __name__, os.path.join("data", str(relative))
    )


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


def walk_with_excludes(
    path: Union[Path, str], excludes: List[str] = None
) -> Iterator[Tuple[str, List[str], List[str]]]:
    """
    Behaves like os.walk but attempts to skip iterations that would enter
    directories we want to exclude (and thus not traverse).
    """

    if excludes is None:
        excludes = EXCLUDES

    for root, dirnames, filenames in os.walk(str(path)):
        dirs = root.split(os.sep)

        # don't yield any directories that have an excluded path
        if any(x in dirs for x in excludes):
            continue

        yield root, dirnames, filenames
