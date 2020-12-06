
"""
datazen - A centralized store for runtime data.
"""

# built-in
from collections import defaultdict
import logging
from typing import Tuple

# internal
from datazen.classes.base_environment import dep_slug_unwrap
from datazen.classes.compile_environment import CompileEnvironment
from datazen.classes.group_environment import GroupEnvironment
from datazen.classes.render_environment import RenderEnvironment

LOG = logging.getLogger(__name__)


class Environment(CompileEnvironment, RenderEnvironment, GroupEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """

    def __init__(self):
        """ Add a notion of 'visited' targets to the environment data. """

        super().__init__()
        self.visited = defaultdict(bool)
        self.default = "compiles"

    def execute(self, target: str = "") -> Tuple[bool, bool]:
        """ Execute an arbitrary target. """

        # resolve a default target if one wasn't provided
        data = self.manifest["data"]
        if not target:
            if "default_target" in data:
                target = data["default_target"]
                LOG.info("using default target '%s'", target)
            elif self.default in data and data[self.default]:
                target = data[self.default][0]["name"]
                LOG.info("resolving first target '%s'", target)

        slug = dep_slug_unwrap(target, self.default)
        return self.handle_task(slug[0], slug[1])

    def compile(self, target: str) -> Tuple[bool, bool]:
        """ Execute a named 'compile' target from the manifest. """

        return self.handle_task("compiles", target)

    def render(self, target: str) -> Tuple[bool, bool]:
        """ Execute a named 'render' target from the manifest. """

        return self.handle_task("renders", target)


def from_manifest(manifest_path: str) -> Environment:
    """ Load an environment object from a schema definition on disk. """

    env = Environment()

    # load the manifest
    if not env.load_manifest_with_cache(manifest_path):
        LOG.error("couldn't load manifest at '%s'", manifest_path)

    return env
