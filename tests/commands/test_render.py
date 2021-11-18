"""
datazen - Tests for the 'render' command interface.
"""

from datazen.commands.compile import str_compile

# module under test
from datazen.commands.render import cmd_render

# internal
from .. import ENV
from ..resources import get_tempfile, get_test_templates


def test_render():
    """Test the 'render' command entry."""

    # compile monolithic yaml
    config_out = get_tempfile(".yaml")
    with open(config_out, "w", encoding="utf-8") as config_file:
        config_file.write(str_compile(ENV.get_configs(True), "yaml"))

    # render yaml from yaml configs
    assert cmd_render(
        get_test_templates(True), "a", config_out, get_tempfile(".yaml")
    )

    # compile monolithic json
    config_out = get_tempfile(".json")
    with open(config_out, "w", encoding="utf-8") as config_file:
        config_file.write(str_compile(ENV.get_configs(True), "json"))

    # render json from json configs
    assert cmd_render(
        get_test_templates(True), "a", config_out, get_tempfile(".json")
    )
