
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
    """ Test the 'compile' command entry. """

    config_dirs = get_test_configs(True)
    schema_dirs = get_test_schemas(True)
    variable_dirs = get_test_variables(True)

    yaml_out = get_tempfile(".yaml")
    assert cmd_compile(config_dirs, schema_dirs, variable_dirs, yaml_out)
    json_out = get_tempfile(".json")
    assert cmd_compile(config_dirs, schema_dirs, variable_dirs, json_out)
    toml_out = get_tempfile(".toml")
    assert not cmd_compile(config_dirs, schema_dirs, variable_dirs,
                           toml_out)


def test_invalid_compile():
    """ Test the off-nominal paths for the 'compile' command. """

    config_dirs = get_test_configs(False)
    schema_dirs = get_test_schemas(False)
    variable_dirs = get_test_variables(False)

    yaml_out = get_tempfile(".yaml")
    assert not cmd_compile(config_dirs, schema_dirs, variable_dirs,
                           yaml_out)
