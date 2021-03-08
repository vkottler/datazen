
"""
datazen - Tests for the 'paths' API.
"""

# module under test
from datazen.paths import unflatten_dict, format_resolve_delims


def test_unflatten_dict():
    """ Test unflatten dict scenarios. """

    assert unflatten_dict({"a.b.c": "test"}) == {"a": {"b": {"c": "test"}}}

    data = {0: "a", "0": {"a.b.c": "test"}, "1": [{"a.b.c": "test"}]}
    expect = {0: "a", "0": {"a": {"b": {"c": "test"}}},
              "1": [{"a": {"b": {"c": "test"}}}]}
    assert unflatten_dict(data) == expect


def test_format_resolve_delims():
    """ Test custom format-String resolution. """

    assert format_resolve_delims("test", {}) == "test"
    assert format_resolve_delims("{a}", {"a": 5}) == "5"
    assert format_resolve_delims("a{a}a", {"a": 5}) == "a5a"
    assert format_resolve_delims("a{a.b.c}a", {"a.b.c": 5}) == "a5a"
