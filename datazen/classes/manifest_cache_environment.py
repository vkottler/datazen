
"""
datazen - A class for adding caching to the manifest-loading environment.
"""

# built-in
import logging
import os
import shutil
from typing import Dict, List, Tuple

# internal
from datazen.classes.manifest_environment import ManifestEnvironment
from datazen.paths import get_file_name
from datazen.load import load_dir_only
from datazen import DEFAULT_MANIFEST, DEFAULT_TYPE, CACHE_SUFFIX
from datazen.compile import str_compile

LOG = logging.getLogger(__name__)


def manifest_cache_dir(path: str, manifest: dict) -> str:
    """ Find a manifest cache (path) from its path and data. """

    cache_name = ".{}{}".format(get_file_name(path), CACHE_SUFFIX)
    default_cache_dir = os.path.join(manifest["dir"], cache_name)

    # set 'cache_dir' to the default if it wasn't set already
    if "cache_dir" not in manifest["data"]:
        manifest["data"]["cache_dir"] = default_cache_dir

    return os.path.abspath(manifest["data"]["cache_dir"])


class ManifestCacheEnvironment(ManifestEnvironment):
    """ A wrapper for the cache functionality for an environment. """

    def load_manifest_with_cache(self, path: str = DEFAULT_MANIFEST) -> bool:
        """
        Load a manifest and its cache, or set up a new cache if one doesn't
        exist.
        """

        result = self.load_manifest(path)

        # if we successfully loaded this manifest, try to load its cache
        if result:
            self.manifest["cache_dir"] = manifest_cache_dir(path,
                                                            self.manifest)
            os.makedirs(self.manifest["cache_dir"], exist_ok=True)
            self.manifest["cache"] = load_dir_only(self.manifest["cache_dir"])
            self.cache_loaded = True

        return result and self.cache_loaded

    def clean_cache(self) -> None:
        """ Remove cached data from the file-system. """

        if "cache_dir" in self.manifest:
            self.unload_all()
            self.manifest["cache"] = {}
            shutil.rmtree(self.manifest["cache_dir"])
            os.makedirs(self.manifest["cache_dir"])
            LOG.info("cleaning cache at '%s'", )

    def write_cache(self) -> None:
        """ Commit cached data to the file-system. """

        if self.cache_loaded:
            for key, val in self.manifest["cache"].items():
                key_path = os.path.join(self.manifest["cache_dir"],
                                        "{}.{}".format(key, DEFAULT_TYPE))
                key_data = str_compile(val, DEFAULT_TYPE)
                with open(key_path, "w") as key_file:
                    key_file.write(key_data)

    def get_hashes(self, sub_dir: str) -> Dict[str, str]:
        """ Get the cached, dictionary of file hashes for a certain key. """

        cache = self.manifest["cache"]

        if "hashes" not in cache:
            cache["hashes"] = {}
        hashes = cache["hashes"]

        if sub_dir not in hashes:
            hashes[sub_dir] = {}

        return hashes[sub_dir]

    def get_loaded(self, sub_dir: str) -> List[str]:
        """ Get the cached, list of loaded files for a certain key. """

        cache = self.manifest["cache"]

        if "loaded" not in cache:
            cache["loaded"] = {}
        loaded = cache["loaded"]

        if sub_dir not in loaded:
            loaded[sub_dir] = []

        return loaded[sub_dir]

    def get_cache_data(self, name: str) -> Tuple[List[str], Dict[str, str]]:
        """ Get the tuple version of cached data. """

        return (self.get_loaded(name), self.get_hashes(name))

    def cached_load_variables(self) -> dict:
        """ Load variables, proxied through the cache. """

        var_data = self.get_cache_data("variables")
        return self.load_variables(var_data[0], var_data[1])

    def cached_load_schemas(self, require_all: bool = True) -> dict:
        """ Load schemas, proxied through the cache. """

        schema_data = self.get_cache_data("schemas")
        return self.load_schemas(require_all, schema_data[0], schema_data[1])

    def cached_enforce_schemas(self, data: dict,
                               require_all: bool = True) -> bool:
        """ Enforce schemas, proxied through the cache. """

        schema_data = self.get_cache_data("schemas")
        return self.enforce_schemas(data, require_all, schema_data[0],
                                    schema_data[1])

    def cached_load_configs(self) -> dict:
        """ Load configs, proxied through the cache. """

        return self.load_configs(self.get_cache_data("configs"),
                                 self.get_cache_data("variables"),
                                 self.get_cache_data("schemas"))
