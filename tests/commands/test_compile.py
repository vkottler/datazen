
"""
datazen - Tests for the 'compile' command interface.
"""

# module under test
from datazen.commands.compile import cmd_compile

# internal
from ..resources import (
    get_test_configs,
    get_test_schemas,
    get_test_variables,
    get_tempfile,
)


def test_compile():
    """ TODO """

    config_dirs = get_test_configs(True)
    schema_dirs = get_test_schemas(True)
    variable_dirs = get_test_variables(True)

    yaml_out = get_tempfile(".yaml")
    assert cmd_compile(config_dirs, schema_dirs, variable_dirs, yaml_out.name)
    json_out = get_tempfile(".json")
    assert cmd_compile(config_dirs, schema_dirs, variable_dirs, json_out.name)
