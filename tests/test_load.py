"""
datazen - Test the 'load' module.
"""

# module under test
from datazen.load import data_added


def test_data_added():
    """Test that the 'data_added' method works."""

    with data_added("a", 1) as data:
        assert data["a"] == 1
