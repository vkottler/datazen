"""
datazen - A class for adding manifest-loading to environments.
"""

# built-in
import logging
import os
from io import StringIO
from typing import List, Tuple

# third-party
from cerberus import Validator

# internal
from datazen.classes.config_environment import ConfigEnvironment
from datazen.classes.target_resolver import TargetResolver
from datazen.classes.template_environment import TemplateEnvironment
from datazen.parsing import load as load_raw
from datazen.parsing import load_stream, merge_dicts
from datazen.paths import get_package_data, get_package_dir, resolve_dir
from datazen.schemas import load_types, inject_custom_schemas
from datazen import DEFAULT_DIR, ROOT_NAMESPACE

LOG = logging.getLogger(__name__)


def get_output_dir(
    data: dict, rel_path: str, default: str = DEFAULT_DIR
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
    data: dict, rel_path: str, default: str = DEFAULT_DIR
) -> None:
    """Set the 'output_dir' key correctly on a dictionary."""

    out_dir = get_output_dir(data, rel_path, default)
    os.makedirs(out_dir, exist_ok=True)
    data["output_dir"] = out_dir


class ManifestEnvironment(ConfigEnvironment, TemplateEnvironment):
    """
    A wrapper for the manifest-loading implementations of an environment.
    """

    def __init__(self):
        """Add a manifest dictionary to the environment."""

        super().__init__()
        self.manifest = {}
        self.target_resolver = TargetResolver()

    def load_dirs(
        self,
        data: dict,
        rel_path: str,
        namespace: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
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
            elif os.path.isdir(os.path.join(rel_path, key)):
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

    def load_manifest_reent(
        self, path: str, manifest_dir: str, params: dict, files: List[str]
    ) -> Tuple[dict, bool]:
        """
        Load a manifest recursively by resolving includes and merging the
        results.
        """

        if not os.path.isabs(path):
            path = os.path.join(manifest_dir, path)
        files.append(os.path.abspath(path))

        # load raw data
        curr_manifest, loaded = load_raw(path, params, {})

        # update params, load again so we can use self-referential params
        if "params" in curr_manifest:
            params = merge_dicts([params, curr_manifest["params"]])
            curr_manifest, loaded = load_raw(path, params, {})

        if not loaded:
            return curr_manifest, False

        # load the data directories before resolving includes
        rel_path = os.path.dirname(path)
        self.load_dirs(curr_manifest, rel_path, allow_dup=True)

        # resolve includes
        all_manifests = [curr_manifest]
        if "includes" in curr_manifest:
            for include in curr_manifest["includes"]:
                result = self.load_manifest_reent(
                    include, rel_path, params, files
                )
                if not result[1]:
                    LOG.info("include '%s' failed to load", path)
                    return curr_manifest, False
                all_manifests.append(result[0])

        # merge include data
        curr_manifest = merge_dicts(all_manifests)

        return curr_manifest, True

    def load_manifest(self, path: str = "manifest.yaml") -> bool:
        """Attempt to load manifest data from a file."""

        # don't allow double-loading manifests
        if self.manifest:
            LOG.error(
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
            path, manifest_dir, {}, files
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
        if not validate_manifest(self.manifest["data"]):
            self.set_valid(False)
            return self.get_valid()

        # add directories parsed from the schema, paths in the manifest are
        # relative to the directory the manifest is located
        rel_path = self.manifest["dir"]
        set_output_dir(self.manifest["data"], rel_path)

        return self.get_valid()


def get_manifest_schema(require_all: bool = True) -> Validator:
    """Load the schema for manifest from the package."""

    rel_path = os.path.join("schemas", "manifest.yaml")
    schema_str = get_package_data(rel_path)
    return Validator(
        load_stream(StringIO(schema_str), rel_path)[0], require_all=require_all
    )


def validate_manifest(manifest: dict) -> bool:
    """Validate manifest data against the package schema."""

    custom_schemas = load_types([get_package_dir("schema_types")])

    with inject_custom_schemas(custom_schemas):
        schema = get_manifest_schema(False)
        result = schema.validate(manifest)

    if not result:
        LOG.error("invalid manifest: %s", schema.errors)

    return result
