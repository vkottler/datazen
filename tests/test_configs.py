"""
datazen - Tests for the 'configs' API.
"""

# internal
from . import ENV


def test_load_configs():
    """Test that the configuration data can be loaded."""

    config_data = ENV.get_configs(True)

    expected = {"a": "a", "b": "b", "c": "c"}

    assert config_data["a"] == expected
    assert config_data["b"] == expected
    assert config_data["c"] == expected

    assert config_data["d"]["d"] == "d"
    assert config_data["d"]["d"] == "d"
    assert config_data["e"]["e"] == "e"
    assert config_data["f"]["f"] == "f"

    assert config_data["yaml"] == "yaml"
    assert config_data["json"] == "json"
