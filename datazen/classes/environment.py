
"""
datazen - A centralized store for runtime data.
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
from datazen.parsing import update_dict_from_stream
from datazen.paths import get_package_data

LOG = logging.getLogger(__name__)


class Environment(ConfigEnvironment, TemplateEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """


def get_manifest_schema(require_all: bool = True) -> Validator:
    """ Load the schema for manifest from the package. """

    rel_path = os.path.join("schemas", "manifest.yaml")
    schema_str = get_package_data(rel_path)
    schema_data = update_dict_from_stream(StringIO(schema_str), rel_path, {})
    return Validator(schema_data, require_all=require_all)


def from_manifest(manifest_path: str) -> Environment:
    """ Load an environment object from a schema definition on disk. """

    env = Environment()

    # load the manifest
    manifest_path = os.path.abspath(manifest_path)
    manifest_data = load_raw(manifest_path, {}, {})

    # enforce the manifest schema
    schema = get_manifest_schema()
    if not schema.validate(manifest_data):
        LOG.error("invalid manifest: %s", schema.errors)
        env.valid = False
        return env

    # add directories parsed from the schema, paths in the manifest are
    # relative to the directory the manifest is located
    rel_path = os.path.dirname(manifest_path)
    env.add_config_dirs(manifest_data["configs"], rel_path)
    env.add_schema_dirs(manifest_data["schemas"], rel_path)
    env.add_template_dirs(manifest_data["templates"], rel_path)
    env.add_variable_dirs(manifest_data["variables"], rel_path)

    return env
