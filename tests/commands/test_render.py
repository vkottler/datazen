
"""
datazen - Tests for the 'render' command interface.
"""

# module under test
from datazen.commands.render import cmd_render
from datazen.commands.compile import str_compile

# internal
from .. import ENV
from ..resources import get_test_templates, get_tempfile


def test_render():
    """ Test the 'render' command entry. """

    # compile monolithic yaml
    config_out = get_tempfile(".yaml")
    with open(config_out, "w") as config_file:
        config_file.write(str_compile(ENV.get_configs(True), "yaml"))

    # render yaml from yaml configs
    assert cmd_render(get_test_templates(True), "a", config_out,
                      get_tempfile(".yaml"))

    # compile monolithic json
    config_out = get_tempfile(".json")
    with open(config_out, "w") as config_file:
        config_file.write(str_compile(ENV.get_configs(True), "json"))

    # render json from json configs
    assert cmd_render(get_test_templates(True), "a", config_out,
                      get_tempfile(".json"))
