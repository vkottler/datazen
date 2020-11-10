
"""
datazen - An environment extension that exposes compilation capabilities.
"""

# built-in
import logging
import os

# internal
from datazen.classes.manifest_cache_environment import ManifestCacheEnvironment
from datazen.compile import str_compile, get_compile_output
from datazen.paths import advance_dict_by_path

LOG = logging.getLogger(__name__)


class CompileEnvironment(ManifestCacheEnvironment):
    """ Leverages a cache-equipped environment to perform compilations. """

    def valid_compile(self, entry: dict, namespace: str) -> bool:
        """ Perform the compilation specified by the entry. """

        path, output_type = get_compile_output(entry)

        # load configs early to update cache
        data = self.cached_load_configs(namespace)

        # advance the dict if it was requested
        if "index_path" in entry:
            data = advance_dict_by_path(entry["index_path"].split("."), data)

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
