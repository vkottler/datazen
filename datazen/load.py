"""
datazen - APIs for loading data from directory trees.
"""

# built-in
from collections import defaultdict
from contextlib import contextmanager
import logging
import os
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Tuple, cast

# third-party
from vcorelib.dict import GenericStrDict
from vcorelib.io.types import LoadResult
from vcorelib.paths import Pathlike, get_file_name, normalize

# internal
from datazen import GLOBAL_KEY
from datazen.parsing import load as load_raw_resolve
from datazen.parsing import set_file_hash
from datazen.paths import (
    advance_dict_by_path,
    get_path_list,
    walk_with_excludes,
)

LOG = logging.getLogger(__name__)


class LoadedFiles(NamedTuple):
    """
    A collection of data for files loaded at runtime (or, a continuation of
    this information loaded from a cache).
    """

    files: Optional[List[str]] = None
    file_data: Optional[Dict[str, GenericStrDict]] = None


DEFAULT_LOADS = LoadedFiles()


@contextmanager
def data_added(
    key: Any, value: Any, data: GenericStrDict = None
) -> Iterator[GenericStrDict]:
    """Inject a key-value pair into a dictionary, in a context."""

    if data is None:
        data = {}

    data[key] = value
    try:
        yield data
    finally:
        del data[key]


def meld_and_resolve(
    path: Pathlike,
    existing_data: GenericStrDict,
    variables: GenericStrDict,
    globals_added: bool = False,
    expect_overwrite: bool = False,
    is_template: bool = True,
    **kwargs,
) -> bool:
    """
    Meld dictionary data from a file into an existing dictionary, assume
    existing data is a template and attempt to resolve variables.
    """

    variables_root: GenericStrDict = variables

    # allow directory/.{file_type} to be equivalent to directory.{file_type}
    key = get_file_name(path)
    if not key:
        data_dict = existing_data
    else:
        if key not in existing_data:
            existing_data[key] = {}
        data_dict = existing_data[key]
        if key in variables:
            variables = variables[key]

    # meld the data
    global_add_success: bool = False
    if globals_added:
        if GLOBAL_KEY not in variables:
            variables[GLOBAL_KEY] = variables_root[GLOBAL_KEY]
            global_add_success = True

    result = load_raw_resolve(
        path, variables, data_dict, expect_overwrite, is_template, **kwargs
    )

    if global_add_success:
        del variables[GLOBAL_KEY]

    return result.success


def load_dir(
    path: Pathlike,
    existing_data: GenericStrDict,
    variables: GenericStrDict = None,
    loads: LoadedFiles = DEFAULT_LOADS,
    expect_overwrite: bool = False,
    are_templates: bool = True,
    logger: logging.Logger = LOG,
) -> LoadResult:
    """Load a directory tree into a dictionary, optionally meld."""

    if variables is None:
        variables = {}

    total_errors = 0
    path = normalize(path)
    for root, _, files in walk_with_excludes(path):
        logger.debug("loading '%s'", root)

        path_list = get_path_list(os.path.abspath(path), root)
        variable_data = advance_dict_by_path(path_list, variables)

        # expose data globally, if it was provided
        added_globals: bool = False
        if GLOBAL_KEY not in variable_data:
            variable_data[GLOBAL_KEY] = variables
            added_globals = True
        else:
            logger.info(
                "can't add 'global' data to '%s', key was already found",
                root,
            )

        # extend the provided list of files that were newly loaded, or at
        # least have new content
        new = load_files(
            cast(List[Pathlike], files),
            root,
            (
                advance_dict_by_path(path_list, existing_data),
                variable_data,
                added_globals,
            ),
            loads.file_data,
            expect_overwrite,
            are_templates,
        )

        if new[1]:
            logger.warning("%d errors loading '%s'.", new[1], root)
        total_errors += new[1]

        if loads.files is not None:
            loads.files.extend(new[0])

        if added_globals:
            del variable_data[GLOBAL_KEY]

    return LoadResult(existing_data, total_errors == 0)


def load_dir_only(
    path: Pathlike,
    expect_overwrite: bool = False,
    are_templates: bool = True,
    logger: logging.Logger = LOG,
) -> LoadResult:
    """
    A convenient wrapper for loading just directory data from a path without
    worrying about melding data, resolving variables, enforcing schemas, etc.
    """

    return load_dir(
        path,
        defaultdict(dict),
        None,
        DEFAULT_LOADS,
        expect_overwrite,
        are_templates,
        logger,
    )


def load_files(
    file_paths: List[Pathlike],
    root: str,
    meld_data: Tuple[GenericStrDict, GenericStrDict, bool],
    hashes: Dict[str, GenericStrDict] = None,
    expect_overwrite: bool = False,
    are_templates: bool = True,
) -> Tuple[List[str], int]:
    """
    Load files into a dictionary and return a list of the files that are
    new or had hash mismatches.
    """

    new_or_changed = []
    errors = 0

    # load (or meld) data
    for name in file_paths:
        name = str(name)
        full_path = os.path.join(root, name)
        assert os.path.isabs(full_path)
        success = meld_and_resolve(
            full_path,
            meld_data[0],
            meld_data[1],
            meld_data[2],
            expect_overwrite,
            are_templates,
        )
        errors += int(not success)
        if success and hashes is not None:
            success = set_file_hash(hashes, full_path)
        if success:
            new_or_changed.append(full_path)

    return new_or_changed, errors
