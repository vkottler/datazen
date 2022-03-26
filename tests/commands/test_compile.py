"""
datazen - Tests for the 'compile' command interface.
"""

# built-in
from contextlib import ExitStack

# module under test
from datazen.commands.compile import cmd_compile

# internal
from ..resources import (
    get_tempfile,
    get_test_configs,
    get_test_schemas,
    get_test_variables,
)


def test_compile():
    """Test the 'compile' command entry."""

    config_dirs = get_test_configs(True)
    schema_dirs = get_test_schemas(True)
    variable_dirs = get_test_variables(True)

    with ExitStack() as stack:
        yaml_out = stack.enter_context(get_tempfile(".yaml"))
        assert cmd_compile(config_dirs, schema_dirs, variable_dirs, yaml_out)
        json_out = stack.enter_context(get_tempfile(".json"))
        assert cmd_compile(config_dirs, schema_dirs, variable_dirs, json_out)
        toml_out = stack.enter_context(get_tempfile(".toml"))
        assert cmd_compile(config_dirs, schema_dirs, variable_dirs, toml_out)
        asdf_out = stack.enter_context(get_tempfile(".asdf"))
        assert not cmd_compile(
            config_dirs, schema_dirs, variable_dirs, asdf_out
        )


def test_invalid_compile():
    """Test the off-nominal paths for the 'compile' command."""

    config_dirs = get_test_configs(False)
    schema_dirs = get_test_schemas(False)
    variable_dirs = get_test_variables(False)

    with get_tempfile(".yaml") as yaml_out:
        assert not cmd_compile(
            config_dirs, schema_dirs, variable_dirs, yaml_out
        )
