
"""
datazen - A class for exposing the capability to run concrete tasks against
          the current environment.
"""

# built-in
from collections import defaultdict
import logging
from typing import List, Tuple

# internal
from datazen import ROOT_NAMESPACE
from datazen.classes.manifest_environment import set_output_dir
from datazen.classes.base_environment import get_dep_slug, dep_slug_unwrap
from datazen.classes.manifest_cache_environment import ManifestCacheEnvironment

LOG = logging.getLogger(__name__)


class TaskEnvironment(ManifestCacheEnvironment):
    """
    Adds capability for running tasks (including tasks with dependencies)
    and tracking whether or not updates are required.
    """

    def valid_noop(self, entry: dict, namespace: str, _: dict = None) -> bool:
        """ Default handle for a potentially-unregistered operation. """

        LOG.error("('%s') '%s' no handler found (default: '%s')",
                  namespace, entry["name"], self.default)
        return False

    def __init__(self):
        """ Add a notion of 'visited' targets to the environment data. """

        super().__init__()
        self.visited = defaultdict(bool)
        self.default = "noop"
        self.handles = defaultdict(lambda: self.valid_noop)

    def is_resolved(self, operation: str, target: str) -> bool:
        """
        Determine whether a target for an operation has already been resolved.
        """

        return self.visited[get_dep_slug(operation, target)]

    def resolve(self, operation: str, target: str) -> None:
        """ Set a target for an operation as resolved. """

        self.visited[get_dep_slug(operation, target)] = True

    def push_deps(self, dep_dict: dict, task_stack:
                  List[Tuple[str, str]], curr_target: str) -> None:
        """ Push dependencies onto a stack if they need to be resolved. """

        for dep in dep_dict:
            dep_tup = dep_slug_unwrap(dep, self.default)
            if dep != curr_target and not self.is_resolved(dep_tup[0],
                                                           dep_tup[1]):
                task_stack.append(dep_tup)

    def handle_task(self, key_name: str, target: str,
                    task_stack: List[Tuple[str, str]] = None) -> bool:
        """
        Handle the setup for manifest tasks, such as loading additional data
        directories and setting the correct output directory.
        """

        if task_stack is None:
            task_stack = []

        entries = self.manifest["data"][key_name]
        for data in entries:
            if target == data["name"]:
                # skip targets we know we've resolved
                if self.is_resolved(key_name, target):
                    return True

                LOG.info("executing '%s'", get_dep_slug(key_name, target))

                # push dependencies first
                if "dependencies" in data:
                    self.push_deps(data["dependencies"], task_stack, target)

                # resolve dependencies first
                while task_stack:
                    task = task_stack.pop()
                    if not self.handle_task(task[0], task[1], task_stack):
                        return False

                # resolve the output directory
                set_output_dir(data, self.manifest["dir"],
                               self.manifest["data"]["output_dir"])

                # load additional data directories if specified
                namespace = self.get_namespace(key_name, target, data)
                self.load_dirs(data, self.manifest["dir"], namespace, True)

                # make sure this namespace is valid
                if not self.get_valid(namespace):
                    LOG.info("namespace '%s' is invalid!", namespace)
                    return False

                # write-through to the cache when we complete an operation,
                # if it succeeded
                result = self.handles[key_name](data, namespace, None)
                if result:
                    self.resolve(key_name, target)
                    self.write_cache()
                    if namespace != ROOT_NAMESPACE:
                        self.restore_cache()
                return result

        return False
