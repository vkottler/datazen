"""
datazen - A module implementing various data-file encoders.
"""

# built-in
from configparser import ConfigParser
from io import StringIO
import json

# third-party
from ruamel.yaml import YAML


def encode_json(configs: dict, ostream: StringIO) -> None:
    """Write config data as JSON to the output stream."""

    json.dump(configs, ostream, indent=2, sort_keys=True)


def encode_yaml(configs: dict, ostream: StringIO) -> None:
    """Write config data as YAML to the output stream."""

    YAML(typ="safe").dump(configs, ostream)


def encode_ini(configs: dict, ostream: StringIO) -> None:
    """Write config data as INI to the output stream."""

    cparser = ConfigParser(interpolation=None)
    cparser.read_dict(configs)
    cparser.write(ostream)
