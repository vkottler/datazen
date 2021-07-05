"""
datazen - A command implementation for compiling configuration data and
          variables into a single, monolithic output.
"""

# built-in
import logging
from typing import List

# internal
from datazen.classes.environment import Environment
from datazen.parsing import get_file_ext
from datazen.compile import str_compile

LOG = logging.getLogger(__name__)


def cmd_compile(
    config_dirs: List[str],
    schema_dirs: List[str],
    variable_dirs: List[str],
    output_file_path: str,
) -> bool:
    """
    Load configuration data by resolving variables and validating provided
    schemas. Write the result to the specified output file, inferring the type
    by the file extension.
    """

    env = Environment()

    # add directories
    env.add_config_dirs(config_dirs)
    env.add_schema_dirs(schema_dirs)
    env.add_variable_dirs(variable_dirs)

    # load data (resolves variables and enforces schemas)
    configs = env.load_configs()
    if not env.configs_valid:
        return False

    # get extension
    ext = get_file_ext(output_file_path)

    # serialize the data
    result = str_compile(configs, ext)
    if not result:
        LOG.error(
            "can't write '%s' data to '%s', no output", ext, output_file_path
        )
        return False

    # write the output
    with open(output_file_path, "w") as output:
        output.write(result)
    LOG.info("wrote '%s' configuration data to '%s'", ext, output_file_path)

    return True
