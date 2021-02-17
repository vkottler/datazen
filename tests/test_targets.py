
"""
datazen - Test functions in the 'targets' module.
"""

# module under test
from datazen.targets import parse_target


def test_parse_target_basic():
    """ Test some simple pattern-matching cases. """

    regex, keys = parse_target("test-{named}-target")
    assert "named" in keys
    assert regex.fullmatch("test-hello-target") is not None

    regex, keys = parse_target("{test1}-{test2}")
    assert "test1" in keys
    assert "test2" in keys
    assert regex.fullmatch("asdf-asdf") is not None

    regex, keys = parse_target("literal_target")
    assert not keys
    assert regex.fullmatch("literal_target") is not None
