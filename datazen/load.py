
"""
datazen - APIs for loading data from directory trees.
"""

# built-in
import logging
import os

# internal
from datazen.parsing import get_file_name
from datazen.parsing import load as load_raw
from datazen.parsing import load_and_resolve as load_raw_resolve

LOG = logging.getLogger(__name__)


def meld_and_resolve(full_path: str, existing_data: dict,
                     variables: dict = None) -> None:
    """
    Meld dictionary data from a file into an existing dictionary, assume
    existing data is a template and attempt to resolve variables.
    """

    if variables is None:
        variables = {}

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
    if variables:
        load_raw_resolve(full_path, variables, data_dict)
    else:
        load_raw(full_path, data_dict)


def load_dir(path: str, existing_data: dict = None,
             variables: dict = None) -> dict:
    """ Load a directory tree into a dictionary, optionally meld. """

    if existing_data is None:
        existing_data = {}

    if variables is None:
        variables = {}

    root_base = os.path.basename(os.path.abspath(path))
    for root, _, files in os.walk(path):
        iter_data = existing_data
        variable_data = variables
        iter_root = root
        iter_base = os.path.basename(iter_root)

        # populate the correct path
        LOG.debug("loading '%s'", root)
        while iter_base != root_base:
            iter_root = os.path.dirname(iter_root)

            # advance iteration data by key, or use an empty dictionary as a
            # placeholder
            try:
                iter_data = iter_data[iter_base]
            except KeyError:
                iter_data[iter_base] = {}
                iter_data = iter_data[iter_base]

            # advance variable data by key, or use an empty dictionary as a
            # placeholder
            try:
                variable_data = variable_data[iter_base]
            except KeyError:
                variable_data[iter_base] = {}
                variable_data = variable_data[iter_base]

            iter_base = os.path.basename(iter_root)

        # load (or meld) data
        for name in files:
            meld_and_resolve(os.path.join(root, name), iter_data,
                             variable_data)

    return existing_data
