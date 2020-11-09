
"""
datazen - A base class to be extended for runtime data loading and storing.
"""

# built-in
import logging
from typing import Dict, List, Tuple
from typing import Optional as Opt

# internal
from datazen import ROOT_NAMESPACE
from datazen.enums import DataType
from datazen.classes.environment_namespace import EnvironmentNamespace, clone

# python3.9 regression: https://github.com/PyCQA/pylint/issues/3882
# pylint: disable=unsubscriptable-object
LOADTYPE = Tuple[Opt[List[str]], Opt[Dict[str, str]]]
# pylint: enable=unsubscriptable-object

LOG = logging.getLogger(__name__)


class BaseEnvironment:
    """ The base class for environment loading-and-storing management. """

    def __init__(self, default_ns: str = ROOT_NAMESPACE):
        """
        Manage environments by names, set up a dictionary with a root
        namespace.
        """

        self.namespaces = {}
        self.namespaces[default_ns] = EnvironmentNamespace()

    def add_namespace(self, name: str, clone_root: bool = True) -> None:
        """ Add a new namespace, optionally clone from the existing root. """

        self.namespaces[name] = EnvironmentNamespace()
        if clone_root:
            clone(self.namespaces[ROOT_NAMESPACE], self.namespaces[name])

    def get_valid(self, name: str = ROOT_NAMESPACE) -> bool:
        """ Get the 'valid' flag for a namespace. """

        return self.namespaces[name].valid

    def set_valid(self, value: bool, name: str = ROOT_NAMESPACE) -> None:
        """ Set the 'valid' flag for a namespace. """

        self.namespaces[name].valid = value

    def get_to_load(self, dir_type: DataType,
                    name: str = ROOT_NAMESPACE) -> List[str]:
        """ Proxy for a namespace's get_to_load. """

        return self.namespaces[name].get_to_load(dir_type)

    def get_data(self, dir_type: DataType, name: str = ROOT_NAMESPACE) -> dict:
        """ Get the raw data for a directory type from a namespace. """

        return self.namespaces[name].data[dir_type]

    def unload_all(self, name: str = ROOT_NAMESPACE) -> None:
        """ Unload all of the directories for a namespace. """

        return self.namespaces[name].unload_all()

    def update_load_state(self, dir_type: DataType, to_load: List[str],
                          name: str = ROOT_NAMESPACE) -> int:
        """ Proxy for update_load_state for a namespace. """

        return self.namespaces[name].update_load_state(dir_type, to_load)

    def add_dir(self, dir_type: DataType, dir_path: str,
                rel_path: str = ".", name: str = ROOT_NAMESPACE) -> bool:
        """ Proxy for add_dir for a namespace. """

        return self.namespaces[name].add_dir(dir_type, dir_path, rel_path)

    def add_dirs(self, dir_type: DataType, dir_paths: List[str],
                 rel_path: str = ".", name: str = ROOT_NAMESPACE) -> int:
        """ Proxy for add_dirs for a namespace. """

        return self.namespaces[name].add_dirs(dir_type, dir_paths, rel_path)
