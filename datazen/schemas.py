"""
datazen - Top-level APIs for loading and interacting with schema definitions.
"""

# built-in
from contextlib import contextmanager
from typing import List, Dict, Iterator
import logging

# third-party
from cerberus import Validator, rules_set_registry

# internal
from datazen.load import load_dir
from datazen.classes.valid_dict import ValidDict

LOG = logging.getLogger(__name__)


def load(
    directories: List[str],
    require_all: bool = True,
    loaded_list: List[str] = None,
    hashes: Dict[str, dict] = None,
) -> dict:
    """Load schemas from a list of directories."""

    result: dict = {}

    # load raw data
    for directory in directories:
        load_dir(directory, result, None, loaded_list, hashes)

    # interpret all top-level keys as schemas
    schemas = {}
    for item in result.items():
        schemas[item[0]] = Validator(item[1], require_all=require_all)
    return schemas


def add_global_schemas(schema_data: Dict[str, dict]) -> None:
    """Add schema-type registrations, globally."""

    for key, schema in schema_data.items():
        LOG.debug("adding '%s' schema type", key)
        rules_set_registry.add(key, schema)


def remove_global_schemas(schema_data: Dict[str, dict]) -> None:
    """Remove schema-type registrations by key name."""

    if schema_data:
        LOG.debug("removing schema types '%s'", ", '".join(schema_data.keys()))
        rules_set_registry.remove(*schema_data.keys())


def load_types(
    directories: List[str],
    loaded_list: List[str] = None,
    hashes: Dict[str, dict] = None,
) -> Dict[str, dict]:
    """Load schema types and optionally register them."""

    schema_data: Dict[str, dict] = {}

    # load raw data
    for directory in directories:
        load_dir(directory, schema_data, None, loaded_list, hashes)
    return schema_data


def validate(schema_data: Dict[str, Validator], data: dict) -> bool:
    """
    For every top-level key in the schema data, attempt to validate the
    provided data.
    """

    for item in schema_data.items():
        key = item[0]
        if key in data:
            if not ValidDict(key, data[key], item[1]).valid:
                return False

    # warn if anything wasn't validated
    for item in data.keys():
        if item not in schema_data:
            LOG.warning("no schema for '%s', not validating", item)

    return True


@contextmanager
def inject_custom_schemas(
    schema_data: Dict[str, dict], should_inject: bool = True
) -> Iterator[None]:
    """
    Allow the user to more easily control adding and removing global schema
    definitions.
    """

    try:
        if should_inject:
            add_global_schemas(schema_data)
        yield
    finally:
        if should_inject:
            remove_global_schemas(schema_data)
