
"""
datazen - Tests for the 'variables' API.
"""

# module under test
from datazen.variables import load as load_variables

# internal
from .resources import get_test_variables


def test_load_variables():
    """ Test that the variable data can be loaded. """

    assert load_variables([get_test_variables()])
