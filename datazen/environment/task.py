"""
datazen - A class for exposing the capability to run concrete tasks against
          the current environment.
"""

# built-in
from collections import defaultdict
from copy import deepcopy
import logging
import os
from time import perf_counter_ns
from typing import Callable, Dict, List, Optional, Tuple

# third-party
from vcorelib.dict import merge

# internal
from datazen import ROOT_NAMESPACE
from datazen.classes.task_data_cache import TaskDataCache
from datazen.environment.base import Task, TaskResult, dep_slug_unwrap
from datazen.environment.manifest import set_output_dir
from datazen.environment.manifest_cache import ManifestCacheEnvironment

LOG = logging.getLogger(__name__)

TaskFunction = Callable[..., TaskResult]


class TaskEnvironment(ManifestCacheEnvironment):
    """
    Adds capability for running tasks (including tasks with dependencies)
    and tracking whether or not updates are required.
    """

    def valid_noop(
        self,
        entry: dict,
        _: str,
        __: dict = None,
        ___: List[str] = None,
        logger: logging.Logger = LOG,
    ) -> TaskResult:
        """Default handle for a potentially-unregistered operation."""

        logger.error(
            "'%s' no handler found (default: '%s')",
            entry["name"],
            self.default,
        )
        return TaskResult(False, False)

    def __init__(self):
        """Add a notion of 'visited' targets to the environment data."""

        super().__init__()
        self.visited = defaultdict(bool)
        self.is_new = defaultdict(bool)
        self.default = "noop"
        self.handles: Dict[str, TaskFunction] = defaultdict(
            lambda: self.valid_noop
        )
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
            return self.visited[Task(operation, target).slug]

    def is_task_new(self, operation: str, target: str) -> bool:
        """Determine if a target has been newly executed this iteration."""

        with self.lock:
            return self.is_new[Task(operation, target).slug]

    def resolve(
        self, operation: str, target: str, should_cache: bool, is_new: bool
    ) -> None:
        """Set a target for an operation as resolved."""

        task = Task(operation, target)
        with self.lock:
            self.visited[task.slug] = True
            self.is_new[task.slug] = is_new
            if should_cache:
                self.write_cache()

    def push_dep(
        self, dep: str, task_stack: List[Task], curr_target: str
    ) -> None:
        """Push a dependency onto a stack if they need to be resolved."""

        task = dep_slug_unwrap(dep, self.default)
        is_new = self.is_task_new(task.variant, task.name)
        is_resolved = self.is_resolved(task.variant, task.name)
        if dep != curr_target and (not is_resolved or is_new):
            task_stack.append(task)

    def get_dep_data(
        self,
        dep_list: List[str],
        logger: logging.Logger = LOG,
    ) -> dict:
        """
        From a list of dependencies, create a dictionary with any task data
        they've saved.
        """

        dep_data: dict = {}

        # flatten all of the tasks' data into a single dict
        for dep in dep_list:
            task = dep_slug_unwrap(dep, self.default)

            with self.lock:
                curr_data = deepcopy(self.task_data[task.variant][task.name])

            if isinstance(curr_data, dict):
                dep_data = merge(dep_data, curr_data, logger=logger)

        return dep_data

    def already_satisfied(
        self,
        target: str,
        output_path: Optional[str],
        load_deps: List[str],
        deps_changed: List[str] = None,
        load_checks: Dict[str, List[str]] = None,
        logger: logging.Logger = LOG,
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
                logger.debug("%s: %s updates detected", target, deps_changed)
            if newly_loaded != 0:
                logger.debug(
                    "%s: %d file updates detected", target, newly_loaded
                )

        return result

    def resolve_dependencies(
        self,
        dep_list: List[str],
        task_stack: List[Task],
        target: str,
        logger: logging.Logger = LOG,
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
                result = self.handle_task(
                    task.variant, task.name, task_stack, False
                )
                self.logger = self.logger_init

                # if a dependency failed, propagate it up
                if not result.success:
                    return False, {}, []
                # otherwise if a dependency was updated
                # (performed), capture it in a list
                if result.fresh or self.is_task_new(task.variant, task.name):
                    deps_changed.append(task.slug)

        # provide dependency data as "flattened"
        return True, self.get_dep_data(dep_list, logger), deps_changed

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
        task_stack: List[Task] = None,
        should_cache: bool = True,
    ) -> TaskResult:
        """
        Handle the setup for manifest tasks, such as loading additional data
        directories and setting the correct output directory.
        """

        task = Task(key_name, target)
        logger = logging.getLogger(task.slug)
        self.logger = logger

        # fall back on default behavior if the manifest doesn't even have
        # an entry for this key
        if key_name not in self.manifest["data"]:
            return self.handles[key_name](
                {"name": ""}, ROOT_NAMESPACE, logger=logger
            )

        if task_stack is None:
            task_stack = []

        data = self.get_manifest_entry(key_name, target)

        if data["name"] is None:
            logger.error("no '%s' found", task.slug)
            return TaskResult(False, False)

        if self.is_resolved(key_name, target):
            return TaskResult(True, False, 0)

        logger.debug("executing '%s'", task.slug)

        # push dependencies
        dep_result = self.resolve_dependencies(
            get_dep_list(data), task_stack, target, logger
        )
        if not dep_result[0]:
            return TaskResult(False, False)

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
            logger.info("namespace '%s' is invalid!", namespace)
            return TaskResult(False, False)

        # write-through to the cache when we complete an operation,
        # if it succeeded
        start = perf_counter_ns()
        result = self.handles[key_name](
            data, namespace, dep_result[1], dep_result[2], logger=logger
        )
        if result.success:
            self.resolve(key_name, target, should_cache, result.fresh)

        # Update the execution time and log the result.
        result = result.with_time(perf_counter_ns() - start)
        result.log(task, logger)
        return result


def get_dep_list(entry: dict) -> List[str]:
    """From task data, build a list of task dependencies."""

    result = []
    for key in ["dependencies", "children"]:
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
