
"""
datazen - Tests for the 'templates' API.
"""

# internal
from .resources import get_test_templates


def test_load_templates():
    """ Test that the templates can be loaded. """

    assert get_test_templates()
