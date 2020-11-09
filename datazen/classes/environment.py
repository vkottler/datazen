
"""
datazen - A centralized store for runtime data.
"""

# built-in
from copy import deepcopy
import logging

# internal
from datazen.classes.manifest_cache_environment import ManifestCacheEnvironment
from datazen.compile import str_compile, get_compile_output

LOG = logging.getLogger(__name__)


class Environment(ManifestCacheEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """

    def valid_compile(self, entry: dict) -> bool:
        """ Perform the compilation specified by the entry. """

        path, output_type = get_compile_output(entry)

        # check if this actually needs to be done, if not, short-circuit
        # and return true

        mode = "a" if "append" in entry and entry["append"] else "w"
        with open(path, mode) as out_file:
            out_file.write(str_compile(self.cached_load_configs(),
                                       output_type))

        return True

    def handle_task(self, key_name: str, target: str) -> bool:
        """
        Handle the setup for manifest tasks, such as loading additional data
        directories and setting the correct output directory.
        """

        if self.manifest and self.valid:
            entries = self.manifest["data"][key_name]
            for data in entries:
                if target == data["name"]:
                    # clone the existing environment so that we can potentially
                    # load new directories and not merge the new data or
                    # results to the original, upstream environment
                    new_env = clone(self)
                    manifest_data = new_env.manifest["data"]

                    # resolve the output directory
                    new_env.set_output_dir(data, new_env.manifest["dir"],
                                           manifest_data["output_dir"])

                    # load additional data directories if specified
                    new_env.load_dirs(data, new_env.manifest["dir"])

                    handles = {
                        "compiles": new_env.valid_compile,
                        "renders": new_env.valid_render,
                    }

                    result = handles[key_name](data)

                    # write-through to the cache when we complete an operation,
                    # if it succeeded
                    if result:
                        self.write_cache()

                    return result

        return False

    def compile(self, target: str) -> bool:
        """ Execute a named 'compile' target from the manifest. """

        return self.handle_task("compiles", target)

    def valid_render(self, render_entry: dict) -> bool:
        """ Perform the render specified by the entry. """

        LOG.info(self.manifest["path"])
        LOG.info(render_entry)

        # resolve dependencies

        return True

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


def clone(env: Environment) -> Environment:
    """ Create a clone (deep copy) of an existing Environment. """

    new_env = Environment()

    # all we need to do is copy all of the attributes
    new_env.directories = deepcopy(env.directories)
    new_env.data = deepcopy(env.data)
    new_env.configs_valid = env.configs_valid
    new_env.valid = env.valid
    new_env.manifest = deepcopy(env.manifest)

    return new_env
