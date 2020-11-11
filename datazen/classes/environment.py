
"""
datazen - A centralized store for runtime data.
"""

# built-in
from collections import defaultdict
import logging
from typing import List, Tuple

# internal
from datazen import ROOT_NAMESPACE
from datazen.classes.base_environment import get_dep_slug
from datazen.classes.manifest_environment import set_output_dir
from datazen.classes.compile_environment import CompileEnvironment
from datazen.classes.render_environment import RenderEnvironment

LOG = logging.getLogger(__name__)


class Environment(CompileEnvironment, RenderEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """

    def __init__(self):
        """ Add a notion of 'visited' targets to the environment data. """

        super().__init__()
        self.visited = defaultdict(bool)

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
        """
        Push (compilation) dependencies onto a stack if they need to be
        resolved.
        """

        for dep in dep_dict:
            if dep != curr_target and not self.is_resolved("compiles", dep):
                task_stack.append(("compiles", dep))

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

                handles = {"compiles": self.valid_compile,
                           "renders": self.valid_render}

                # write-through to the cache when we complete an operation,
                # if it succeeded
                result = handles[key_name](data, namespace)
                if result:
                    self.resolve(key_name, target)
                    self.write_cache()
                    if namespace != ROOT_NAMESPACE:
                        self.restore_cache()
                return result

        return False

    def compile(self, target: str) -> bool:
        """ Execute a named 'compile' target from the manifest. """

        return self.handle_task("compiles", target)

    def render(self, target: str) -> bool:
        """ Execute a named 'render' target from the manifest. """

        return self.handle_task("renders", target)


def from_manifest(manifest_path: str) -> Environment:
    """ Load an environment object from a schema definition on disk. """

    env = Environment()

    # load the manifest
    if not env.load_manifest_with_cache(manifest_path):
        LOG.error("couldn't load manifest at '%s'", manifest_path)

    return env
