
"""
datazen - An interface for turning a dictionary into various serialized forms.
"""

# built-in
import json
import logging

# third-party
from ruamel import yaml

LOG = logging.getLogger(__name__)


def str_compile(configs: dict, data_type: str) -> str:
    """
    Serialize dictionary data into the String-form of a specific,
    serializeable type.
    """

    # serialize the data
    if data_type == "json":
        result = json.dumps(configs, indent=4)
    elif data_type == "yaml":
        raw_result = yaml.dump(configs)
        result = raw_result if raw_result else ""
    else:
        LOG.error("can't serialize '%s' data (unknown type)", data_type)
        return ""

    return result
