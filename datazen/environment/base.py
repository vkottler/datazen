"""
datazen - A base class to be extended for runtime data loading and storing.
"""

# built-in
from collections import defaultdict
import logging
from typing import Dict, List, Tuple, Optional
import threading

# internal
from datazen import ROOT_NAMESPACE
from datazen.enums import DataType
from datazen.environment import EnvironmentNamespace, clone

LOADTYPE = Tuple[Optional[List[str]], Optional[Dict[str, dict]]]
LOG = logging.getLogger(__name__)
SLUG_DELIM = "-"


def get_dep_slug(operation: str, name: str) -> str:
    """Build a key-slug for an operation's target."""

    return f"{operation}{SLUG_DELIM}{name}"


def dep_slug_unwrap(slug: str, default_op: str) -> Tuple[str, str]:
    """
    From a slug String, determine the operation + target pair, if the
    operation isn't specified use a default.
    """

    result = (default_op, slug)
    if SLUG_DELIM in slug:
        split = slug.split(SLUG_DELIM, 1)
        result = (split[0], split[1])
    return result


class BaseEnvironment:
    """The base class for environment loading-and-storing management."""

    def __init__(self, default_ns: str = ROOT_NAMESPACE):
        """
        Manage environments by names, set up a dictionary with a root
        namespace.
        """

        self.namespaces = {}
        self.namespaces[default_ns] = EnvironmentNamespace()
        self.lock = threading.RLock()

    def add_namespace(self, name: str, clone_root: bool = True) -> None:
        """Add a new namespace, optionally clone from the existing root."""

        with self.lock:
            self.namespaces[name] = EnvironmentNamespace()
            if clone_root and name != ROOT_NAMESPACE:
                clone(self.namespaces[ROOT_NAMESPACE], self.namespaces[name])

    def get_valid(self, name: str = ROOT_NAMESPACE) -> bool:
        """Get the 'valid' flag for a namespace."""

        return self.namespaces[name].valid

    def set_valid(self, value: bool, name: str = ROOT_NAMESPACE) -> None:
        """Set the 'valid' flag for a namespace."""

        self.namespaces[name].valid = value

    def get_to_load(
        self, dir_type: DataType, name: str = ROOT_NAMESPACE
    ) -> List[str]:
        """Proxy for a namespace's get_to_load."""

        return self.namespaces[name].get_to_load(dir_type)

    def get_data(self, dir_type: DataType, name: str = ROOT_NAMESPACE) -> dict:
        """Get the raw data for a directory type from a namespace."""

        return self.namespaces[name].data[dir_type]

    def unload_all(self, name: str = ROOT_NAMESPACE) -> None:
        """Unload all of the directories for a namespace."""

        return self.namespaces[name].unload_all()

    def update_load_state(
        self,
        dir_type: DataType,
        to_load: List[str],
        name: str = ROOT_NAMESPACE,
    ) -> int:
        """Proxy for update_load_state for a namespace."""

        return self.namespaces[name].update_load_state(dir_type, to_load)

    def add_dir(
        self,
        dir_type: DataType,
        dir_path: str,
        rel_path: str = ".",
        name: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
    ) -> bool:
        """Proxy for add_dir for a namespace."""

        return self.namespaces[name].add_dir(
            dir_type, dir_path, rel_path, allow_dup
        )

    def add_dirs(
        self,
        dir_type: DataType,
        dir_paths: List[str],
        rel_path: str = ".",
        name: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
    ) -> int:
        """Proxy for add_dirs for a namespace."""

        return self.namespaces[name].add_dirs(
            dir_type, dir_paths, rel_path, allow_dup
        )

    def get_namespace(
        self, key_name: str, target: str, target_data: dict
    ) -> str:
        """
        Determine the namespace that a target should use, in general they
        all should be unique unless they don't load anything new.
        """

        load_deps = defaultdict(list)
        schema_deps = ["schemas", "schema_types"]
        load_deps["compiles"] = ["configs", "variables"] + schema_deps
        load_deps["renders"] = ["templates"]

        # add a unique namespace for this target if it loads
        # any new data as to not load any of this data upstream,
        # but still cache it (edge cases here?)
        load_dep_list = load_deps[key_name]
        for load_dep in load_dep_list:
            if load_dep in target_data:
                namespace = get_dep_slug(key_name, target)
                self.add_namespace(namespace)
                return namespace

        # don't make a new namespace if we don't load
        # new data
        return ROOT_NAMESPACE
