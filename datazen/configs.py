
"""
datazen - Top-level APIs for loading and interacting with configuration data.
"""

# built-in
import logging
from typing import List

# internal
from datazen.load import load_dir

LOG = logging.getLogger(__name__)


def load(directories: List[str], variable_data: dict = None,
         loaded_list: List[str] = None) -> dict:
    """ Load configuration data from a list of directories. """

    result: dict = {}
    for directory in directories:
        LOG.info("loading configs from '%s'", directory)
        load_dir(directory, result, variable_data, loaded_list)
    return result
