
"""
datazen - A class for adding manifest-loading to environments.
"""

# built-in
import logging
import os
from io import StringIO

# third-party
from cerberus import Validator  # type: ignore

# internal
from datazen.classes.config_environment import ConfigEnvironment
from datazen.classes.template_environment import TemplateEnvironment
from datazen.parsing import load as load_raw
from datazen.parsing import load_stream
from datazen.paths import get_package_data, resolve_dir
from datazen import DEFAULT_DIR, ROOT_NAMESPACE

LOG = logging.getLogger(__name__)


def get_output_dir(data: dict, rel_path: str,
                   default: str = DEFAULT_DIR) -> str:
    """
    Get the resolved output directory based on a dictionary containing
    target data.
    """

    # turn the output directory into a valid path
    out_dir = default
    if "output_dir" in data:
        out_dir = data["output_dir"]
    return resolve_dir(out_dir, rel_path)


def set_output_dir(data: dict, rel_path: str,
                   default: str = DEFAULT_DIR) -> None:
    """ Set the 'output_dir' key correctly on a dictionary. """

    out_dir = get_output_dir(data, rel_path, default)
    os.makedirs(out_dir, exist_ok=True)
    data["output_dir"] = out_dir
    LOG.info("using output directory to '%s'", out_dir)


class ManifestEnvironment(ConfigEnvironment, TemplateEnvironment):
    """
    A wrapper for the manifest-loading implementations of an environment.
    """

    def __init__(self):
        """ Add a manifest dictionary to the environment. """

        super().__init__()
        self.manifest = {}

    def load_dirs(self, data: dict, rel_path: str,
                  namespace: str = ROOT_NAMESPACE,
                  allow_dup: bool = False) -> None:
        """
        Looks for keys matching types of directories that can be loaded
        into an environment and tries to load them.
        """

        key_handles = {
            "configs": self.add_config_dirs,
            "schemas": self.add_schema_dirs,
            "templates": self.add_template_dirs,
            "variables": self.add_variable_dirs,
        }
        for key in key_handles:
            if key in data:
                key_handles[key](data[key], rel_path, namespace, allow_dup)
            # if a directory list isn't provided, and the directory of the
            # same name of the key is present in the manifest directory,
            # load it
            elif os.path.isdir(os.path.join(rel_path, key)):
                key_handles[key]([key], rel_path, namespace, allow_dup)
            else:
                LOG.info("not loading any '%s'", key)

    def load_manifest(self, path: str = "manifest.yaml") -> bool:
        """ Attempt to load manifest data from a file. """

        # don't allow double-loading manifests
        if self.manifest:
            LOG.error("manifest '%s' already loaded for this environment",
                      self.manifest["path"])
            return False

        self.manifest["path"] = os.path.abspath(path)
        self.manifest["dir"] = os.path.dirname(self.manifest["path"])
        self.manifest["data"], loaded = load_raw(self.manifest["path"], {}, {})

        # make sure we loaded a manifest
        if not loaded:
            self.set_valid(False)
            return self.get_valid()

        # enforce the manifest schema
        schema = get_manifest_schema(False)
        if not schema.validate(self.manifest["data"]):
            LOG.error("invalid manifest: %s", schema.errors)
            self.set_valid(False)
            return self.get_valid()

        # add directories parsed from the schema, paths in the manifest are
        # relative to the directory the manifest is located
        rel_path = self.manifest["dir"]
        set_output_dir(self.manifest["data"], rel_path)

        # load the data directories
        self.load_dirs(self.manifest["data"], rel_path)

        return self.get_valid()


def get_manifest_schema(require_all: bool = True) -> Validator:
    """ Load the schema for manifest from the package. """

    rel_path = os.path.join("schemas", "manifest.yaml")
    schema_str = get_package_data(rel_path)
    return Validator(load_stream(StringIO(schema_str), rel_path)[0],
                     require_all=require_all)
