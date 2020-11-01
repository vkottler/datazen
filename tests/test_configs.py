
"""
datazen - Tests for the 'configs' API.
"""

# module under test
from datazen.configs import load as load_configs
from datazen.variables import load as load_variables

# internal
from .resources import get_test_configs, get_test_variables


def test_load_configs():
    """ Test that the configuration data can be loaded. """

    variable_data = load_variables([get_test_variables()])
    assert variable_data

    config_data = load_configs([get_test_configs()], variable_data)
    assert config_data

    assert config_data["a"]["a"] == "a"
    assert config_data["b"]["b"] == "b"
    assert config_data["c"]["c"] == "c"
    assert config_data["d"]["d"] == "d"
    assert config_data["d"]["d"] == "d"
    assert config_data["e"]["e"] == "e"
    assert config_data["f"]["f"] == "f"

    assert config_data["yaml"] == "test"
    assert config_data["json"] == "test"
