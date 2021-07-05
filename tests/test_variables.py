"""
datazen - Tests for the 'variables' API.
"""

# internal
from . import ENV


def test_load_variables():
    """Test that the variable data can be loaded."""

    assert ENV.get_variables(True)


def test_load_invalid_variables():
    """Test that invalid data returns False."""

    assert not ENV.get_variables(False)["bad"]
    assert not ENV.get_configs(False)
    assert not ENV.invalid.configs_valid
