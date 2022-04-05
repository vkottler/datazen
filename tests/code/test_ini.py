"""
datazen - Test encoding and decoding of INI files and data.
"""

# internal
from tests.resources import scoped_scenario


def test_ini_basic():
    """Test some compile targets that interact with INI data."""

    with scoped_scenario("test_ini") as env:
        for key in "abc":
            assert env.compile(f"single-{key}").success
        assert not env.compile("bad").success
