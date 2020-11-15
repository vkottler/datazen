
"""
datazen - Top-level APIs for loading and interacting with schema definitions.
"""

# built-in
from typing import List, Dict

# third-party
from cerberus import Validator  # type: ignore

# internal
from datazen.load import load_dir
from datazen.classes.valid_dict import ValidDict


def load(directories: List[str], require_all: bool = True,
         loaded_list: List[str] = None,
         hashes: Dict[str, dict] = None) -> dict:
    """ Load schemas from a list of directories. """

    result: dict = {}

    # load raw data
    for directory in directories:
        load_dir(directory, result, None, loaded_list, hashes)

    # interpret all top-level keys as schemas
    schemas = {}
    for item in result.items():
        schemas[item[0]] = Validator(item[1], require_all=require_all)
    return schemas


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

    return True
