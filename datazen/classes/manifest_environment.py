
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
from datazen.paths import get_package_data

LOG = logging.getLogger(__name__)


class ManifestEnvironment(ConfigEnvironment, TemplateEnvironment):
    """
    A wrapper for the manifest-loading implementations of an environment.
    """

    def load_manifest(self, path: str = "manifest.yaml") -> bool:
        """ Attempt to load manifest data from a file. """

        # don't allow double-loading manifests
        if self.manifest:
            LOG.error("manifest '%s' already loaded for this environment",
                      self.manifest["path"])
            return False

        self.manifest["path"] = os.path.abspath(path)
        self.manifest["data"] = load_raw(self.manifest["path"], {}, {})

        # enforce the manifest schema
        schema = get_manifest_schema(False)
        if not schema.validate(self.manifest["data"]):
            LOG.error("invalid manifest: %s", schema.errors)
            self.valid = False
            return self.valid

        # resolve the default output directory
        if "output_directory" not in self.manifest["data"]:
            default_dir = os.path.dirname(self.manifest["path"])
            self.manifest["data"]["output_directory"] = default_dir

        # create the output directory, if necessary
        LOG.info("using output directory '%s'",
                 self.manifest["data"]["output_directory"])
        os.makedirs(self.manifest["data"]["output_directory"], exist_ok=True)

        # add directories parsed from the schema, paths in the manifest are
        # relative to the directory the manifest is located
        rel_path = os.path.dirname(self.manifest["path"])

        key_handles = {
            "configs": self.add_config_dirs,
            "schemas": self.add_schema_dirs,
            "templates": self.add_template_dirs,
            "variables": self.add_variable_dirs,
        }
        for key in key_handles:
            if key in self.manifest["data"]:
                key_handles[key](self.manifest["data"][key], rel_path)
            # if a directory list isn't provided, and the directory of the
            # same name of the key is present in the manifest directory,
            # load it
            elif os.path.isdir(os.path.join(rel_path, key)):
                key_handles[key]([key], rel_path)
            else:
                LOG.info("not loading any '%s'", key)

        return self.valid


def get_manifest_schema(require_all: bool = True) -> Validator:
    """ Load the schema for manifest from the package. """

    rel_path = os.path.join("schemas", "manifest.yaml")
    schema_str = get_package_data(rel_path)
    return Validator(load_stream(StringIO(schema_str), rel_path),
                     require_all=require_all)
