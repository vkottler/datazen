"""
datazen - APIs for loading raw data from files.
"""

# built-in
import hashlib
from io import StringIO
import logging
from pathlib import Path
import time
from typing import List, Union

# third-party
import jinja2

# internal
from datazen.code import ARBITER
from datazen.code.types import DataStream, LoadResult
from datazen.paths import get_file_ext

LOG = logging.getLogger(__name__)


def load_stream(
    data_stream: DataStream,
    path: Union[Path, str],
    logger: logging.Logger = LOG,
    **kwargs,
) -> LoadResult:
    """
    Load arbitrary data from a text stream, update an existing dictionary.
    """

    return ARBITER.decode_stream(
        get_file_ext(path), data_stream, logger, **kwargs
    )


def dedup_dict_lists(data: dict) -> dict:
    """
    Finds list elements in a dictionary and removes duplicate entries, mutates
    the original list.
    """

    for key in data:
        if isinstance(data[key], dict):
            data[key] = dedup_dict_lists(data[key])
        elif isinstance(data[key], list):
            new_list = []
            for item in data[key]:
                if item not in new_list:
                    new_list.append(item)
            data[key] = new_list

    return data


def merge_dicts(
    dicts: List[dict],
    expect_overwrite: bool = False,
    logger: logging.Logger = LOG,
) -> dict:
    """
    Merge a list of dictionary data into a single set (mutates the first
    element).
    """

    result = dicts[0]
    for right_dict in dicts[1:]:
        result = merge(
            result,
            right_dict,
            expect_overwrite=expect_overwrite,
            logger=logger,
        )
    return result


def merge(
    dict_a: dict,
    dict_b: dict,
    path: List[str] = None,
    expect_overwrite: bool = False,
    logger: logging.Logger = LOG,
) -> dict:
    """
    Combine two dictionaries recursively, prefers dict_a in a conflict. For
    values of the same key that are lists, the lists are combined. Otherwise
    the resulting dictionary is cleanly merged.
    """

    if path is None:
        path = []

    for key in dict_b:
        if key in dict_a:
            # first try to coerce b's type into a's
            if not isinstance(dict_b[key], type(dict_a[key])):
                try:
                    dict_b[key] = type(dict_a[key])(dict_b[key])
                except ValueError:
                    pass

            # same leaf value
            if dict_a[key] == dict_b[key]:
                pass
            elif isinstance(dict_a[key], dict) and isinstance(
                dict_b[key], dict
            ):
                merge(
                    dict_a[key],
                    dict_b[key],
                    path + [str(key)],
                    expect_overwrite,
                    logger,
                )
            elif isinstance(dict_a[key], list) and isinstance(
                dict_b[key], list
            ):
                dict_a[key].extend(dict_b[key])
            elif not isinstance(dict_b[key], type(dict_a[key])):
                logger.error(
                    "Type mismatch at '%s'", ".".join(path + [str(key)])
                )
                logger.error("left:  %s (%s)", type(dict_a[key]), dict_a[key])
                logger.error("right: %s (%s)", type(dict_b[key]), dict_b[key])
            elif not expect_overwrite:
                logger.error("Conflict at '%s'", ".".join(path + [str(key)]))
                logger.error("left:  %s", dict_a[key])
                logger.error("right: %s", dict_b[key])
            else:
                dict_a[key] = dict_b[key]
        else:
            dict_a[key] = dict_b[key]

    return dict_a


def load(
    path: Union[Path, str],
    variables: dict,
    dict_to_update: dict,
    expect_overwrite: bool = False,
    is_template: bool = True,
    logger: logging.Logger = LOG,
) -> LoadResult:
    """
    Load raw file data and meld it into an existing dictionary. Update
    the result as if it's a template using the provided variables.
    """

    result = LoadResult({}, False)

    # Include the time it takes to initially read or render the file in the
    # returned time.
    start = time.time_ns()
    load_time = 0

    # Read the raw file and interpret it as a template, resolve 'variables'.
    path = str(path)
    try:
        with open(path, encoding="utf-8") as config_file:
            if variables and is_template:
                template = jinja2.Template(config_file.read())
                str_output = template.render(variables)
            else:
                str_output = config_file.read()
        load_time = start - time.time_ns()
    except FileNotFoundError:
        logger.error("can't find '%s' to load file data", path)
        return result
    except jinja2.exceptions.TemplateError as exc:
        logger.error(
            "couldn't render '%s': %s (variables: %s)",
            path,
            exc,
            variables,
        )
        return result

    load_result = load_stream(StringIO(str_output), path, logger)
    return LoadResult(
        merge(
            dict_to_update, load_result.data, expect_overwrite=expect_overwrite
        ),
        load_result.success,
        load_result.time_ns + load_time,
    )


def get_hash(data: str, encoding: str = "utf-8") -> str:
    """Get the MD5 of String data."""

    return hashlib.md5(bytes(data, encoding)).hexdigest()


def get_file_hash(path: Union[Path, str]) -> str:
    """Get the MD5 of a file by path."""

    path = str(path)
    with open(path, encoding="utf-8") as data:
        contents = data.read()
    return get_hash(contents)


def set_file_hash(
    hashes: dict, path: Union[Path, str], set_new: bool = True
) -> bool:
    """Evaluate a hash dictionary and update it on a miss."""

    path = str(path)
    str_hash = get_file_hash(path)
    result = True
    if path in hashes and str_hash == hashes[path]["hash"]:
        result = False
    elif set_new:
        if path not in hashes:
            hashes[path] = {}
        hashes[path]["hash"] = str_hash
        hashes[path]["time"] = time.time()

    return result
