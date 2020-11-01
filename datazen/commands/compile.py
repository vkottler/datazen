
"""
datazen - A command implementation for compiling configuration data and
          variables into a single, monolithic output.
"""

# built-in
import json
import logging
from typing import List

# third-party
from ruamel import yaml

# internal
from datazen.configs import load as load_configs
from datazen.parsing import get_file_ext
from datazen.schemas import load as load_schemas, validate
from datazen.variables import load as load_variables

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


def cmd_compile(config_dirs: List[str], schema_dirs: List[str],
                variable_dirs: List[str], output_file_path: str) -> bool:
    """
    Load configuration data by resolving variables and validating provided
    schemas. Write the result to the specified output file, inferring the type
    by the file extension.
    """

    # load data
    configs = load_configs(config_dirs, load_variables(variable_dirs))

    # load and enforce schemas
    if not validate(load_schemas(schema_dirs, True), configs):
        LOG.info("schema validation on failed")
        return False

    # get extension
    ext = get_file_ext(output_file_path)

    # serialize the data
    result = str_compile(configs, ext)
    if not result:
        LOG.error("can't write '%s' data to '%s', no output", ext,
                  output_file_path)
        return False

    # write the output
    with open(output_file_path, "w") as output:
        output.write(result)
    LOG.info("wrote '%s' configuration data to '%s'", ext, output_file_path)

    return True
