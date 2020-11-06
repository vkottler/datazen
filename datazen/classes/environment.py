
"""
datazen - A centralized store for runtime data.
"""

# built-in
import logging

# internal
from datazen.classes.manifest_environment import ManifestEnvironment

LOG = logging.getLogger(__name__)


class Environment(ManifestEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """

    def compile(self, target: str) -> bool:
        """ Execute a named 'compile' target from the manifest. """

        if self.manifest and self.valid:
            compiles = self.manifest["data"]["compiles"]
            for compile_data in compiles:
                if target == compile_data["name"]:
                    return True

        return False

    def render(self, target: str) -> bool:
        """ Execute a named 'render' target from the manifest. """

        if self.manifest and self.valid:
            renders = self.manifest["data"]["renders"]
            for render_data in renders:
                if target == render_data["name"]:
                    return True

        return False


def from_manifest(manifest_path: str) -> Environment:
    """ Load an environment object from a schema definition on disk. """

    env = Environment()

    # load the manifest
    if not env.load_manifest(manifest_path):
        LOG.error("couldn't load manifest at '%s'", manifest_path)

    return env
