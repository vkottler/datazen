
"""
datazen - Tests for the 'variables' API.
"""

# internal
from . import ENV


def test_load_variables():
    """ Test that the variable data can be loaded. """

    assert ENV.get_variables(True)
