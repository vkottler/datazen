
"""
datazen - Top-level APIs for loading and interacting with variables.
"""

# built-in
import logging
from typing import List, Dict

# internal
from datazen.load import load_dir

LOG = logging.getLogger(__name__)


def load(directories: List[str],
         loaded_list: List[str] = None, hashes: Dict[str, str] = None) -> dict:
    """ Load variable data from a list of directories. """

    result: dict = {}
    for directory in directories:
        LOG.info("loading variables from '%s'", directory)
        load_dir(directory, result, None, loaded_list, hashes)
    return result
