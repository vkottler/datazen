
"""
datazen - APIs for loading data from directory trees.
"""

# built-in
import logging
import os

# internal
from datazen.paths import get_path_list, advance_dict_by_path
from datazen.parsing import get_file_name
from datazen.parsing import load as load_raw_resolve

LOG = logging.getLogger(__name__)
GLOBAL_KEY = "global"


def meld_and_resolve(full_path: str, existing_data: dict, variables: dict,
                     globals_added: bool = False) -> None:
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

    load_raw_resolve(full_path, variables, data_dict)

    if global_add_success:
        del variables[GLOBAL_KEY]


def load_dir(path: str, existing_data: dict = None,
             variables: dict = None) -> dict:
    """ Load a directory tree into a dictionary, optionally meld. """

    if existing_data is None:
        existing_data = {}

    if variables is None:
        variables = {}

    root_abs = os.path.abspath(path)
    for root, _, files in os.walk(path):
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
            msg = "can't add 'global' data to '%s', key was already found"
            LOG.info(msg, root)

        LOG.info(variable_data)

        # load (or meld) data
        for name in files:
            meld_and_resolve(os.path.join(root, name), iter_data,
                             variable_data, added_globals)

        if added_globals:
            del variable_data[GLOBAL_KEY]

    return existing_data
