"""
datazen - An interface for turning a dictionary into various serialized forms.
"""

# built-in
import io
import json
import logging
import os
from typing import Tuple

# third-party
from ruamel.yaml import YAML

# internal
from datazen import DEFAULT_TYPE

LOG = logging.getLogger(__name__)


def write_dir(directory: str, data: dict, out_type: str = "json") -> None:
    """Write dictionary data to the file-system."""

    os.makedirs(directory, exist_ok=True)
    for key, val in data.items():
        key_path = os.path.join(directory, "{}.{}".format(key, out_type))
        with open(key_path, "w") as key_file:
            key_file.write(str_compile(val, out_type))
    os.sync()


def str_compile(configs: dict, data_type: str) -> str:
    """
    Serialize dictionary data into the String-form of a specific,
    serializeable type.
    """

    ostream = io.StringIO()

    # serialize the data
    if data_type == "json":
        result = json.dumps(configs, indent=4, sort_keys=True)
    elif data_type == "yaml":
        YAML(typ="safe").dump(configs, ostream)
        raw_result = ostream.getvalue()
        result = raw_result if raw_result else ""
    else:
        LOG.error("can't serialize '%s' data (unknown type)", data_type)
        return ""

    return result


def get_compile_output(
    entry: dict, default_type: str = DEFAULT_TYPE
) -> Tuple[str, str]:
    """
    Determine the output path and type of a compile target, from the target's
    data.
    """

    # determine the output type
    output_type = default_type
    if "output_type" in entry:
        output_type = entry["output_type"]

    # write the output
    filename = "{}.{}".format(entry["name"], output_type)
    return os.path.join(entry["output_dir"], filename), output_type
