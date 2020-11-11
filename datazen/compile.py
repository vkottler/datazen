
"""
datazen - An interface for turning a dictionary into various serialized forms.
"""

# built-in
import json
import logging
import os
from typing import Tuple

# third-party
from ruamel import yaml

# internal
from datazen import DEFAULT_TYPE

LOG = logging.getLogger(__name__)


def str_compile(configs: dict, data_type: str) -> str:
    """
    Serialize dictionary data into the String-form of a specific,
    serializeable type.
    """

    # serialize the data
    if data_type == "json":
        result = json.dumps(configs, indent=4, sort_keys=True)
    elif data_type == "yaml":
        raw_result = yaml.dump(configs)
        result = raw_result if raw_result else ""
    else:
        LOG.error("can't serialize '%s' data (unknown type)", data_type)
        return ""

    return result


def get_compile_output(entry: dict,
                       default_type: str = DEFAULT_TYPE) -> Tuple[str, str]:
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
