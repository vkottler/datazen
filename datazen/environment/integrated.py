"""
datazen - A centralized store for runtime data.
"""

# built-in
from collections import defaultdict
import logging
import os
from typing import List

# third-party
from vcorelib.logging import log_time

# internal
from datazen import CACHE_SUFFIX
from datazen.environment.base import TaskResult, dep_slug_unwrap
from datazen.environment.command import CommandEnvironment
from datazen.environment.compile import CompileEnvironment
from datazen.environment.group import GroupEnvironment
from datazen.environment.render import RenderEnvironment


class Environment(
    CompileEnvironment, RenderEnvironment, GroupEnvironment, CommandEnvironment
):
    """A wrapper for inheriting all environment-loading capabilities."""

    def __init__(self, newline: str = os.linesep) -> None:
        """Add a notion of 'visited' targets to the environment data."""

        super().__init__(newline=newline)
        self.visited = defaultdict(bool)
        self.default = "compiles"

    def execute(
        self, target: str = "", should_cache: bool = True
    ) -> TaskResult:
        """Execute an arbitrary target."""

        # resolve a default target if one wasn't provided
        data = self.manifest["data"]
        if not target:
            if "default_target" in data:
                target = data["default_target"]
                self.logger.info("using default target '%s'", target)
            elif self.default in data and data[self.default]:
                target = data[self.default][0]["name"]
                self.logger.info("resolving first target '%s'", target)

        slug = dep_slug_unwrap(target, self.default)
        return self.handle_task(slug[0], slug[1], should_cache=should_cache)

    def execute_targets(self, targets: List[str]) -> bool:
        """
        Execute a list of named targets and return whether or not the entire
        set was successful.
        """

        # use a resolved, default target if none are specified
        if not targets and self.default_target():
            targets.append(self.default_target())

        for target in targets:
            with log_time(self.logger, "Target '%s'", target):
                task_result = self.execute(target, False)
                if not task_result[0]:
                    self.logger.error("target '%s' failed", target)
                    return False
                if not task_result[1]:
                    self.logger.info("'%s' already satisfied", target)

        # write the cache at the end, if we were totally successful
        self.write_cache()
        return True

    def group(self, target: str) -> TaskResult:
        """Attempt to satisfy a 'group' target."""

        return self.handle_task("groups", target)

    def compile(self, target: str) -> TaskResult:
        """Execute a named 'compile' target from the manifest."""

        return self.handle_task("compiles", target)

    def render(self, target: str) -> TaskResult:
        """Execute a named 'render' target from the manifest."""

        return self.handle_task("renders", target)

    def command(self, target: str) -> TaskResult:
        """Execute a named 'command' target from the manifest."""

        return self.handle_task("commands", target)


def from_manifest(
    manifest_path: str,
    newline: str = os.linesep,
    data_cache_name: str = "task_data",
    logger: logging.Logger = logging.getLogger(__name__),
) -> Environment:
    """Load an environment object from a schema definition on disk."""

    env = Environment(newline=newline)

    # load the manifest
    if not env.load_manifest_with_cache(manifest_path):
        logger.error("couldn't load manifest at '%s'", manifest_path)
    else:
        data_cache = f".{data_cache_name}{CACHE_SUFFIX}"
        assert env.cache is not None
        path = os.path.join(os.path.dirname(env.cache.cache_dir), data_cache)
        env.init_cache(os.path.abspath(path))

    return env
