
"""
datazen - A centralized store for runtime data.
"""

# built-in
import logging
import os

# internal
from datazen.classes.manifest_environment import set_output_dir
from datazen.classes.manifest_cache_environment import ManifestCacheEnvironment
from datazen.compile import str_compile, get_compile_output

LOG = logging.getLogger(__name__)


class Environment(ManifestCacheEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """

    def valid_compile(self, entry: dict, namespace: str) -> bool:
        """ Perform the compilation specified by the entry. """

        path, output_type = get_compile_output(entry)

        # load configs early to update cache
        data = self.cached_load_configs(namespace)

        # make sure this compilation needs to be performed
        compile_deps = ["configs", "variables", "schemas"]
        if os.path.isfile(path) and self.get_new_loaded(compile_deps) == 0:
            LOG.debug("compile '%s' satisfied, skipping", entry["name"])
            return True

        mode = "a" if "append" in entry and entry["append"] else "w"
        with open(path, mode) as out_file:
            out_file.write(str_compile(data, output_type))
            LOG.info("compiled '%s' data to '%s'", output_type, path)
        return True

    def handle_task(self, key_name: str, target: str) -> bool:
        """
        Handle the setup for manifest tasks, such as loading additional data
        directories and setting the correct output directory.
        """

        if self.manifest and self.get_valid():
            entries = self.manifest["data"][key_name]
            for data in entries:
                if target == data["name"]:
                    # add a unique namespace for this target if it loads
                    # any new data as to not load any of this data upstream,
                    # but still cache it (edge cases here?)
                    #
                    # don't make a new namespace if we don't load
                    # new data
                    namespace = "{}_{}".format(key_name, target)
                    self.add_namespace(namespace)

                    manifest_data = self.manifest["data"]

                    # resolve the output directory
                    set_output_dir(data, self.manifest["dir"],
                                   manifest_data["output_dir"])

                    # load additional data directories if specified
                    self.load_dirs(data, self.manifest["dir"], namespace)

                    handles = {
                        "compiles": self.valid_compile,
                        "renders": self.valid_render,
                    }

                    result = handles[key_name](data, namespace)

                    # write-through to the cache when we complete an operation,
                    # if it succeeded
                    if result:
                        self.write_cache()
                        self.restore_cache()

                    return result

        return False

    def compile(self, target: str) -> bool:
        """ Execute a named 'compile' target from the manifest. """

        return self.handle_task("compiles", target)

    def valid_render(self, render_entry: dict, namespace: str) -> bool:
        """ Perform the render specified by the entry. """

        LOG.info(self.manifest["path"])
        LOG.info(render_entry)
        LOG.info(namespace)

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
