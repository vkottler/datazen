"""
datazen - A class for exposing the capability to run concrete tasks against
          the current environment.
"""

# built-in
from collections import defaultdict
import logging
import os
from typing import List, Tuple, Dict, Optional

# internal
from datazen import ROOT_NAMESPACE
from datazen.classes.manifest_environment import set_output_dir
from datazen.classes.base_environment import get_dep_slug, dep_slug_unwrap
from datazen.classes.manifest_cache_environment import ManifestCacheEnvironment
from datazen.classes.task_data_cache import TaskDataCache

LOG = logging.getLogger(__name__)


class TaskEnvironment(ManifestCacheEnvironment):
    """
    Adds capability for running tasks (including tasks with dependencies)
    and tracking whether or not updates are required.
    """

    def valid_noop(
        self, entry: dict, _: str, __: dict = None, ___: List[str] = None
    ) -> Tuple[bool, bool]:
        """Default handle for a potentially-unregistered operation."""

        LOG.error(
            "'%s' no handler found (default: '%s')",
            entry["name"],
            self.default,
        )
        return False, False

    def __init__(self):
        """Add a notion of 'visited' targets to the environment data."""

        super().__init__()
        self.visited = defaultdict(bool)
        self.is_new = defaultdict(bool)
        self.default = "noop"
        self.handles = defaultdict(lambda: self.valid_noop)
        self.data_cache: Optional[TaskDataCache] = None

    def init_cache(self, cache_dir: str) -> None:
        """Initialize the task-data cache."""

        if self.data_cache is None:
            self.data_cache = TaskDataCache(cache_dir)

    def write_cache(self) -> None:
        """Commit cached data to the file-system."""

        super().write_cache()
        if self.data_cache is not None:
            self.data_cache.save()

    def clean_cache(self, purge_data: bool = True) -> None:
        """Remove cached data from the file-system."""

        super().clean_cache(True)
        if self.data_cache is not None:
            self.data_cache.clean(purge_data)

    @property
    def task_data(self) -> dict:
        """Proxy task data through the cache."""

        assert self.data_cache is not None
        return self.data_cache.data

    def is_resolved(self, operation: str, target: str) -> bool:
        """
        Determine whether a target for an operation has already been resolved.
        """

        with self.lock:
            return self.visited[get_dep_slug(operation, target)]

    def is_task_new(self, operation: str, target: str) -> bool:
        """Determine if a target has been newly executed this iteration."""

        with self.lock:
            return self.is_new[get_dep_slug(operation, target)]

    def resolve(
        self, operation: str, target: str, should_cache: bool, is_new: bool
    ) -> None:
        """Set a target for an operation as resolved."""

        with self.lock:
            self.visited[get_dep_slug(operation, target)] = True
            self.is_new[get_dep_slug(operation, target)] = is_new
            if should_cache:
                self.write_cache()

    def push_dep(
        self, dep: str, task_stack: List[Tuple[str, str]], curr_target: str
    ) -> None:
        """Push a dependency onto a stack if they need to be resolved."""

        dep_tup = dep_slug_unwrap(dep, self.default)
        is_new = self.is_task_new(dep_tup[0], dep_tup[1])
        is_resolved = self.is_resolved(dep_tup[0], dep_tup[1])
        if dep != curr_target and (not is_resolved or is_new):
            task_stack.append(dep_tup)

    def get_dep_data(self, dep_list: List[str]) -> dict:
        """
        From a list of dependencies, create a dictionary with any task data
        they've saved.
        """

        dep_data = {}

        # flatten all of the tasks' data into a single dict
        for dep in dep_list:
            dep_tup = dep_slug_unwrap(dep, self.default)

            with self.lock:
                curr_data = self.task_data[dep_tup[0]][dep_tup[1]]

            if isinstance(curr_data, dict):
                dep_data.update(curr_data)

        return dep_data

    def already_satisfied(
        self,
        target: str,
        output_path: Optional[str],
        load_deps: List[str],
        deps_changed: List[str] = None,
        load_checks: Dict[str, List[str]] = None,
    ) -> bool:
        """
        Check if a target is already satisfied, if not debug-log some
        information about why not.
        """

        is_file = True if output_path is None else os.path.isfile(output_path)
        with self.lock:
            newly_loaded = self.get_new_loaded(load_deps, load_checks)
            result = (
                not self.manifest_changed
                and is_file
                and not deps_changed
                and newly_loaded == 0
            )

        # log less-obvious dependency-resolution hits
        if is_file:
            if deps_changed:
                LOG.debug("%s: %s updates detected", target, deps_changed)
            if newly_loaded != 0:
                LOG.debug("%s: %d file updates detected", target, newly_loaded)

        return result

    def resolve_dependencies(
        self,
        dep_list: List[str],
        task_stack: List[Tuple[str, str]],
        target: str,
    ) -> Tuple[bool, dict, List[str]]:
        """
        Execute the entire chain of dependencies for a task, return the
        aggregate result as a boolean as well as the dependency data and which
        dependencies changed.
        """

        deps_changed = []
        for dep in dep_list:
            self.push_dep(dep, task_stack, target)

            # resolve dependencies
            while task_stack:
                task = task_stack.pop()
                result = self.handle_task(task[0], task[1], task_stack, False)

                # if a dependency failed, propagate it up
                if not result[0]:
                    return False, {}, []
                # otherwise if a dependency was updated
                # (performed), capture it in a list
                if result[1] or self.is_task_new(task[0], task[1]):
                    deps_changed.append(get_dep_slug(task[0], task[1]))

        # provide dependency data as "flattened"
        return True, self.get_dep_data(dep_list), deps_changed

    def get_manifest_entry(self, category: str, name: str) -> dict:
        """Get an entry from the manifest."""

        result: dict = defaultdict(lambda: None)

        with self.lock:
            candidate = self.target_resolver.get_target(category, name)
        if candidate is not None:
            result = candidate

        return result

    def handle_task(
        self,
        key_name: str,
        target: str,
        task_stack: List[Tuple[str, str]] = None,
        should_cache: bool = True,
    ) -> Tuple[bool, bool]:
        """
        Handle the setup for manifest tasks, such as loading additional data
        directories and setting the correct output directory.
        """

        # fall back on default behavior if the manifest doesn't even have
        # an entry for this key
        if key_name not in self.manifest["data"]:
            return self.handles[key_name]({"name": ""}, ROOT_NAMESPACE)

        if task_stack is None:
            task_stack = []

        data = self.get_manifest_entry(key_name, target)

        if data["name"] is None:
            LOG.error("no '%s' found", get_dep_slug(key_name, target))
            return False, False

        if self.is_resolved(key_name, target):
            return True, False

        LOG.debug("executing '%s'", get_dep_slug(key_name, target))

        # push dependencies
        dep_result = self.resolve_dependencies(
            get_dep_list(data), task_stack, target
        )
        if not dep_result[0]:
            return False, False

        # resolve the output directory
        set_output_dir(
            data, self.manifest["dir"], self.manifest["data"]["output_dir"]
        )

        # load additional data directories if specified
        with self.lock:
            namespace = self.get_namespace(key_name, target, data)
            self.load_dirs(data, self.manifest["dir"], namespace, True)

        # make sure this namespace is valid
        if not self.get_valid(namespace):
            LOG.info("namespace '%s' is invalid!", namespace)
            return False, False

        # write-through to the cache when we complete an operation,
        # if it succeeded
        result = self.handles[key_name](
            data, namespace, dep_result[1], dep_result[2]
        )
        if result[0]:
            self.resolve(key_name, target, should_cache, result[1])
        return result


def get_dep_list(entry: dict) -> List[str]:
    """From task data, build a list of task dependencies."""

    result = []
    dep_keys = ["dependencies", "children"]
    for key in dep_keys:
        if key in entry:
            result += entry[key]
    return list(set(result))


def get_path(entry: dict, key: str = "name") -> str:
    """Get the full path to a render output from the manifest entry."""

    path = entry[key]
    if "output_path" in entry:
        path = entry["output_path"]
    if not os.path.isabs(path):
        path = os.path.join(entry["output_dir"], path)
    return path
