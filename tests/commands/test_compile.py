
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
)


def test_compile():
    """ TODO """

    config_dirs = get_test_configs(True)
    schema_dirs = get_test_schemas(True)
    variable_dirs = get_test_variables(True)

    assert cmd_compile(config_dirs, schema_dirs, variable_dirs, "test.yaml")
    assert cmd_compile(config_dirs, schema_dirs, variable_dirs, "test.json")
