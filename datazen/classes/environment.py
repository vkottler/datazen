
"""
datazen - A centralized store for runtime data.
"""

# built-in
import logging
import os
import pkgutil
from io import StringIO

# third-party
from cerberus import Validator  # type: ignore

# internal
from datazen.classes.config_environment import ConfigEnvironment
from datazen.classes.template_environment import TemplateEnvironment
from datazen.parsing import load as load_raw
from datazen.parsing import update_dict_from_stream

LOG = logging.getLogger(__name__)


class Environment(ConfigEnvironment, TemplateEnvironment):
    """ A wrapper for inheriting all environment-loading capabilities. """


def from_manifest(manifest_path: str) -> Environment:
    """ TODO """

    env = Environment()

    manifest_data = load_raw(manifest_path, {}, {})

    # come up with a manifest schema, put it in the repo
    rel_path = os.path.join("data", "schemas", "manifest.yaml")
    schema_raw = pkgutil.get_data("datazen", rel_path)
    schema_bytes = schema_raw if schema_raw else bytes()
    schema_str = schema_bytes.decode("utf-8")

    schema_data = update_dict_from_stream(StringIO(schema_str), rel_path, {})
    schema = Validator(schema_data, True)

    if not schema.validate(manifest_data):
        LOG.error("invalid manifest: %s", schema.errors)
        return env

    # add directories parsed from the schema

    return env
