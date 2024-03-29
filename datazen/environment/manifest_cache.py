"""
datazen - A class for adding caching to the manifest-loading environment.
"""

# built-in
import logging
import os
from typing import Dict, List, Optional

# third-party
import jinja2
from vcorelib.dict import GenericStrDict
from vcorelib.io.types import LoadResult
from vcorelib.paths import get_file_name

# internal
from datazen import CACHE_SUFFIX, DEFAULT_MANIFEST, ROOT_NAMESPACE
from datazen.classes.file_info_cache import FileInfoCache, cmp_total_loaded
from datazen.classes.file_info_cache import copy as copy_cache
from datazen.classes.file_info_cache import meld as meld_cache
from datazen.environment.manifest import ManifestEnvironment

LOG = logging.getLogger(__name__)


def manifest_cache_dir(path: str, manifest: GenericStrDict) -> str:
    """Find a manifest cache (path) from its path and data."""

    cache_name = f".{get_file_name(path)}{CACHE_SUFFIX}"
    default_cache_dir = os.path.join(manifest["dir"], cache_name)

    # set 'cache_dir' to the default if it wasn't set already
    if "cache_dir" not in manifest["data"]:
        manifest["data"]["cache_dir"] = default_cache_dir

    return os.path.abspath(str(manifest["data"]["cache_dir"]))


class ManifestCacheEnvironment(ManifestEnvironment):
    """A wrapper for the cache functionality for an environment."""

    def __init__(self, **kwargs) -> None:
        """Extend the environment with a notion of the cache being loaded."""

        super().__init__(**kwargs)
        self.cache: Optional[FileInfoCache] = None
        self.aggregate_cache: Optional[FileInfoCache] = None
        self.initial_cache: Optional[FileInfoCache] = None
        self.manifest_changed = True

    def load_manifest_with_cache(
        self, path: str = DEFAULT_MANIFEST, logger: logging.Logger = LOG
    ) -> bool:
        """
        Load a manifest and its cache, or set up a new cache if one doesn't
        exist.
        """

        result = self.load_manifest(path)

        # if we successfully loaded this manifest, try to load its cache
        if result:
            self.cache = FileInfoCache(manifest_cache_dir(path, self.manifest))
            self.aggregate_cache = copy_cache(self.cache)

            # correctly set the state of whether or not this manifest
            # has changed
            self.manifest_changed = False
            for mpath in self.manifest["files"]:
                if not self.cache.check_hit(ROOT_NAMESPACE, mpath):
                    self.manifest_changed = True

            # save a copy of the initial cache, so that we can use it to
            # determine if state has changed when evaluating targets
            self.initial_cache = copy_cache(self.cache)
            logger.debug("cache-environment loaded from '%s'", path)

        return result and self.cache is not None

    def clean_cache(self, purge_data: bool = True) -> None:
        """Remove cached data from the file-system."""

        if purge_data:
            for name in self.namespaces:
                self.unload_all(name)
        if self.cache is not None:
            self.cache.clean()
        self.manifest_changed = True

    def write_cache(self) -> None:
        """Commit cached data to the file-system."""

        if self.cache is not None:
            assert self.aggregate_cache is not None
            meld_cache(self.aggregate_cache, self.cache)
            self.aggregate_cache.write()

    def describe_cache(self) -> None:
        """Describe the [initial] cache for debugging purposes."""

        assert self.initial_cache is not None
        self.initial_cache.describe()

    def restore_cache(self) -> None:
        """Return the cache to its initially-loaded state."""

        if self.cache is not None:
            assert self.aggregate_cache is not None
            meld_cache(self.aggregate_cache, self.cache)
            assert self.initial_cache is not None
            self.cache = copy_cache(self.initial_cache)

    def get_new_loaded(
        self, types: List[str], load_checks: Dict[str, List[str]] = None
    ) -> int:
        """
        Compute the number of new files loaded (since the initial load)
        for a set of types;
        """

        assert self.cache is not None
        assert self.initial_cache is not None
        return cmp_total_loaded(
            self.cache, self.initial_cache, types, load_checks
        )

    def cached_load_variables(self, name: str = ROOT_NAMESPACE) -> LoadResult:
        """Load variables, proxied through the cache."""

        assert self.cache is not None
        return self.load_variables(self.cache.get_data("variables"), name)

    def cached_load_schemas(
        self, require_all: bool = True, name: str = ROOT_NAMESPACE
    ) -> GenericStrDict:
        """Load schemas, proxied through the cache."""

        assert self.cache is not None
        return self.load_schemas(
            require_all,
            self.cache.get_data("schemas"),
            self.cache.get_data("schema_types"),
            name,
        )

    def cached_enforce_schemas(
        self,
        data: GenericStrDict,
        require_all: bool = True,
        name: str = ROOT_NAMESPACE,
    ) -> bool:
        """Enforce schemas, proxied through the cache."""

        assert self.cache is not None
        return self.enforce_schemas(
            data,
            require_all=require_all,
            sch_loads=self.cache.get_data("schemas"),
            sch_types_loads=self.cache.get_data("schema_types"),
            name=name,
        )

    def cached_load_configs(
        self, name: str = ROOT_NAMESPACE, enforce_schemas: bool = True
    ) -> LoadResult:
        """Load configs, proxied through the cache."""

        assert self.cache is not None
        return self.load_configs(
            cfg_loads=self.cache.get_data("configs"),
            var_loads=self.cache.get_data("variables"),
            sch_loads=self.cache.get_data("schemas"),
            sch_types_loads=self.cache.get_data("schema_types"),
            name=name,
            enforce_schemas=enforce_schemas,
        )

    def cached_load_templates(
        self, name: str = ROOT_NAMESPACE
    ) -> Dict[str, jinja2.Template]:
        """Load templates, proxied through the cache."""

        assert self.cache is not None
        return self.load_templates(self.cache.get_data("templates"), name)
