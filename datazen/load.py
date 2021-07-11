"""
datazen - APIs for loading data from directory trees.
"""

# built-in
from collections import defaultdict
import logging
import os
from typing import Dict, List, Tuple

# internal
from datazen import GLOBAL_KEY
from datazen.paths import (
    get_path_list,
    advance_dict_by_path,
    walk_with_excludes,
    get_file_name,
)
from datazen.parsing import load as load_raw_resolve
from datazen.parsing import set_file_hash

LOG = logging.getLogger(__name__)


def meld_and_resolve(
    full_path: str,
    existing_data: dict,
    variables: dict,
    globals_added: bool = False,
    expect_overwrite: bool = False,
    is_template: bool = True,
) -> bool:
    """
    Meld dictionary data from a file into an existing dictionary, assume
    existing data is a template and attempt to resolve variables.
    """

    variables_root: dict = variables

    # allow directory/.{file_type} to be equivalent to directory.{file_type}
    key = get_file_name(full_path)
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

    _, loaded = load_raw_resolve(
        full_path, variables, data_dict, expect_overwrite, is_template
    )

    if global_add_success:
        del variables[GLOBAL_KEY]

    return loaded


def load_dir(
    path: str,
    existing_data: dict,
    variables: dict = None,
    loaded_list: List[str] = None,
    hashes: Dict[str, dict] = None,
    expect_overwrite: bool = False,
    are_templates: bool = True,
) -> dict:
    """Load a directory tree into a dictionary, optionally meld."""

    if variables is None:
        variables = {}

    if loaded_list is None:
        loaded_list = []

    if hashes is None:
        hashes = defaultdict(dict)

    root_abs = os.path.abspath(path)
    os.sync()
    for root, _, files in walk_with_excludes(path):
        LOG.debug("loading '%s'", root)

        path_list = get_path_list(root_abs, root)
        iter_data = advance_dict_by_path(path_list, existing_data)
        variable_data = advance_dict_by_path(path_list, variables)

        # expose data globally, if it was provided
        added_globals: bool = False
        if GLOBAL_KEY not in variable_data:
            variable_data[GLOBAL_KEY] = variables
            added_globals = True
        else:
            LOG.info(
                "can't add 'global' data to '%s', key was already found",
                root,
            )

        # extend the provided list of files that were newly loaded, or at
        # least have new content
        loaded_list.extend(
            load_files(
                files,
                root,
                (iter_data, variable_data, added_globals),
                hashes,
                expect_overwrite,
                are_templates,
            )
        )

        if added_globals:
            del variable_data[GLOBAL_KEY]

    return existing_data


def load_dir_only(
    path: str,
    expect_overwrite: bool = False,
    are_templates: bool = True,
) -> dict:
    """
    A convenient wrapper for loading just directory data from a path without
    worrying about melding data, resolving variables, enforcing schemas, etc.
    """

    return load_dir(
        path,
        defaultdict(dict),
        None,
        None,
        None,
        expect_overwrite,
        are_templates,
    )


def load_files(
    file_paths: List[str],
    root: str,
    meld_data: Tuple[dict, dict, bool],
    hashes: Dict[str, dict],
    expect_overwrite: bool = False,
    are_templates: bool = True,
) -> List[str]:
    """
    Load files into a dictionary and return a list of the files that are
    new or had hash mismatches.
    """

    new_or_changed = []

    # load (or meld) data
    for name in file_paths:
        full_path = os.path.join(root, name)
        assert os.path.isabs(full_path)
        if (
            meld_and_resolve(
                full_path,
                meld_data[0],
                meld_data[1],
                meld_data[2],
                expect_overwrite,
                are_templates,
            )
            and set_file_hash(hashes, full_path)
        ):
            new_or_changed.append(full_path)

    return new_or_changed
