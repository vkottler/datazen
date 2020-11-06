
"""
datazen - A centralized store for runtime data.
"""

# built-in
import os
import logging

# internal
from datazen.classes.manifest_environment import ManifestEnvironment
from datazen.compile import str_compile

LOG = logging.getLogger(__name__)


class Environment(ManifestEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """

    def valid_compile(self, output_dir: str, entry: dict) -> bool:
        """ Perform the compilation specified by the entry. """

        # determine the output type
        output_type = "yaml"
        if "output_type" in entry:
            output_type = entry["output_type"]

        # resolve dependencies

        # write the output
        filename = "{}.{}".format(entry["name"], output_type)
        path = os.path.join(output_dir, filename)
        mode = "a" if "append" in entry and entry["append"] else "w"
        with open(path, mode) as out_file:
            out_file.write(str_compile(self.load_configs(), output_type))

        return True

    def handle_task(self, key_name: str, target: str) -> bool:
        """
        Handle the setup for manifest tasks, such as loading additional data
        directories and setting the correct output directory.
        """

        handles = {
            "compiles": self.valid_compile,
            "renders": self.valid_render,
        }

        if self.manifest and self.valid:
            entries = self.manifest["data"][key_name]
            for data in entries:
                if target == data["name"]:

                    # resolve the output directory
                    self.set_output_dir(data, self.manifest["dir"])

                    # load additional data directories if specified

                    return handles[key_name](data["output_dir"], data)

        return False

    def compile(self, target: str) -> bool:
        """ Execute a named 'compile' target from the manifest. """

        return self.handle_task("compiles", target)

    def valid_render(self, output_dir: str, render_entry: dict) -> bool:
        """ Perform the render specified by the entry. """

        LOG.info(self.manifest["path"])
        LOG.info(output_dir)
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
    if not env.load_manifest(manifest_path):
        LOG.error("couldn't load manifest at '%s'", manifest_path)

    return env
