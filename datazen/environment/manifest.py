"""
datazen - A class for adding manifest-loading to environments.
"""

# built-in
import logging
import os
from typing import List, Tuple, Type, cast

# third-party
from vcorelib.dict import GenericDict, GenericStrDict, merge_dicts
from vcorelib.dict.env import dict_resolve_env_vars
from vcorelib.paths import resource
from vcorelib.schemas import CerberusSchema
from vcorelib.schemas.base import Schema

# internal
from datazen import DEFAULT_DIR, PKG_NAME, ROOT_NAMESPACE
from datazen.classes.target_resolver import TargetResolver
from datazen.classes.valid_dict import ValidDict
from datazen.environment.config import ConfigEnvironment
from datazen.environment.template import TemplateEnvironment
from datazen.parsing import load as load_raw
from datazen.paths import resolve_dir
from datazen.schemas import inject_custom_schemas, load_types

LOG = logging.getLogger(__name__)


def get_output_dir(
    data: GenericStrDict, rel_path: str, default: str = DEFAULT_DIR
) -> str:
    """
    Get the resolved output directory based on a dictionary containing
    target data.
    """

    # turn the output directory into a valid path
    out_dir = default
    if "output_dir" in data:
        out_dir = data["output_dir"]
    return resolve_dir(out_dir, rel_path)


def set_output_dir(
    data: GenericStrDict, rel_path: str, default: str = DEFAULT_DIR
) -> None:
    """Set the 'output_dir' key correctly on a dictionary."""

    out_dir = get_output_dir(data, rel_path, default)
    os.makedirs(out_dir, exist_ok=True)
    data["output_dir"] = out_dir


def update_path_relativity(path_strs: List[str], rel_path: str) -> None:
    """
    For a list of paths, if paths aren't absolute, apply the provided relative
    path to the beginning of the path.
    """
    for idx, path in enumerate(path_strs):
        if not os.path.isabs(path):
            path_strs[idx] = os.path.join(rel_path, path)


class ManifestEnvironment(ConfigEnvironment, TemplateEnvironment):
    """
    A wrapper for the manifest-loading implementations of an environment.
    """

    targets_with_paths = ["compiles", "renders"]
    path_fields = [
        "configs",
        "schemas",
        "schema_types",
        "variables",
        "templates",
    ]

    def __init__(self, **kwargs) -> None:
        """Add a manifest dictionary to the environment."""

        super().__init__(**kwargs)
        self.manifest: GenericStrDict = {}
        self.target_resolver = TargetResolver()

    def load_dirs(
        self,
        data: GenericStrDict,
        rel_path: str,
        namespace: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
        load_defaults: bool = True,
    ) -> None:
        """
        Looks for keys matching types of directories that can be loaded
        into an environment and tries to load them.
        """

        key_handles = {
            "configs": self.add_config_dirs,
            "schemas": self.add_schema_dirs,
            "schema_types": self.add_schema_type_dirs,
            "templates": self.add_template_dirs,
            "variables": self.add_variable_dirs,
        }
        for key, handler in key_handles.items():
            if key in data:
                handler(data[key], rel_path, namespace, allow_dup)
            # if a directory list isn't provided, and the directory of the
            # same name of the key is present in the manifest directory,
            # load it
            elif os.path.isdir(os.path.join(rel_path, key)) and load_defaults:
                handler([key], rel_path, namespace, allow_dup)

    def default_target(self) -> str:
        """
        Retrieve a configured default target for a manifest, otherwise an
        empty String.
        """

        result = ""
        if self.get_valid() and "default_target" in self.manifest["data"]:
            result = self.manifest["data"]["default_target"]
        return result

    @staticmethod
    def update_task_dirs(data: GenericStrDict, rel_path: str) -> None:
        """
        Update path definitions in the provided manifest chunk to respect a
        relative path (e.g. the directory that the manifest chunk was loaded
        from).
        """

        # Iterate over all task types that may contain paths.
        for key in ManifestEnvironment.targets_with_paths:
            # Iterate over each task definition.
            for item in data.get(key, []):
                # For each task definition, iterate over fields that may
                # contain paths (if they're specified).
                for path_list in ManifestEnvironment.path_fields:
                    if path_list in item:
                        update_path_relativity(item[path_list], rel_path)

    def load_manifest_reent(
        self,
        path: str,
        manifest_dir: str,
        params: GenericDict,
        files: List[str],
        logger: logging.Logger = LOG,
    ) -> Tuple[GenericStrDict, bool]:
        """
        Load a manifest recursively by resolving includes and merging the
        results.
        """

        if not os.path.isabs(path):
            path = os.path.join(manifest_dir, path)
        files.append(os.path.abspath(path))

        # load raw data
        curr_manifest, loaded, _ = load_raw(path, params, {})

        # update params, load again so we can use self-referential params
        if loaded and "params" in curr_manifest:
            params = merge_dicts(
                [
                    params,
                    dict_resolve_env_vars(
                        cast(GenericDict, curr_manifest["params"])
                    ),
                ]
            )
            curr_manifest, loaded, _ = load_raw(path, params, {})

        if not loaded:
            return curr_manifest, False

        # load the data directories before resolving includes
        rel_path = os.path.dirname(path)
        self.load_dirs(
            curr_manifest,
            rel_path,
            allow_dup=True,
            load_defaults=bool(curr_manifest.get("default_dirs", True)),
        )
        self.update_task_dirs(curr_manifest, rel_path)

        # resolve includes
        all_manifests = [curr_manifest]
        if "includes" in curr_manifest:
            for include in cast(GenericStrDict, curr_manifest["includes"]):
                result = self.load_manifest_reent(
                    include, rel_path, params, files, logger
                )
                if not result[1]:
                    logger.info("include '%s' failed to load", path)
                    return curr_manifest, False
                all_manifests.append(result[0])

        # merge include data
        curr_manifest = merge_dicts(all_manifests, expect_overwrite=True)

        return curr_manifest, True

    def load_manifest(
        self, path: str = "manifest.yaml", logger: logging.Logger = LOG
    ) -> bool:
        """Attempt to load manifest data from a file."""

        # don't allow double-loading manifests
        if self.manifest:
            logger.error(
                "manifest '%s' already loaded for this environment",
                self.manifest["path"],
            )
            return False

        path = os.path.abspath(path)
        manifest_dir = os.path.dirname(path)
        self.manifest["path"] = path
        self.manifest["dir"] = manifest_dir
        files: List[str] = []
        self.manifest["data"], loaded = self.load_manifest_reent(
            path, manifest_dir, {}, files, logger
        )
        self.manifest["files"] = files

        # set up target resolver
        self.target_resolver.clear()
        candidates = ["compiles", "commands", "renders", "groups"]
        for candidate in candidates:
            if candidate in self.manifest["data"]:
                cand_data = self.manifest["data"][candidate]
                self.target_resolver.register_group(candidate, cand_data)

        # make sure we loaded a manifest
        if not loaded:
            self.set_valid(False)
            return self.get_valid()

        # enforce the manifest schema
        if not validate_manifest(self.manifest["data"], logger):
            self.set_valid(False)
            return self.get_valid()

        # add directories parsed from the schema, paths in the manifest are
        # relative to the directory the manifest is located
        rel_path = self.manifest["dir"]
        set_output_dir(self.manifest["data"], rel_path)

        return self.get_valid()


def get_manifest_schema(
    require_all: bool = True,
    cls: Type[Schema] = CerberusSchema,
) -> Schema:
    """Load the schema for manifest from the package."""

    return cls.from_path(
        resource("schemas", "manifest.yaml", package=PKG_NAME),
        require_all=require_all,
    )


def validate_manifest(
    manifest: GenericStrDict, logger: logging.Logger = LOG
) -> bool:
    """Validate manifest data against the package schema."""

    schemas = resource("schema_types", package=PKG_NAME)
    assert schemas is not None

    with inject_custom_schemas(load_types([schemas])):
        result = ValidDict(
            "manifest",
            manifest,
            get_manifest_schema(require_all=False),
            logger=logger,
        )

    return result.valid
