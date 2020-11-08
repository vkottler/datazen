
"""
datazen - A class for adding caching to the manifest-loading environment.
"""

# built-in
import logging
import os
import shutil

# internal
from datazen.classes.manifest_environment import ManifestEnvironment
from datazen.paths import get_file_name
from datazen.load import load_dir_only
from datazen import DEFAULT_MANIFEST, DEFAULT_TYPE
from datazen.compile import str_compile

LOG = logging.getLogger(__name__)


def manifest_cache_dir(path: str, manifest: dict) -> str:
    """ Find a manifest cache (path) from its path and data. """

    cache_name = ".{}_cache".format(get_file_name(path))
    default_cache_dir = os.path.join(manifest["dir"], cache_name)

    # set 'cache_dir' to the default if it wasn't set already
    if "cache_dir" not in manifest["data"]:
        manifest["data"]["cache_dir"] = default_cache_dir

    return os.path.abspath(manifest["data"]["cache_dir"])


class ManifestCacheEnvironment(ManifestEnvironment):
    """ TODO """

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
