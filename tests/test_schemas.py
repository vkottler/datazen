
"""
datazen - Tests for the 'schemas' API.
"""

# module under test
from datazen.schemas import load as load_schemas

# internal
from .resources import get_test_schemas


def test_load_schemas():
    """ Test that the schemas can be loaded. """

    assert load_schemas([get_test_schemas()])
