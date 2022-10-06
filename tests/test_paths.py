"""
datazen - Tests for the 'paths' API.
"""

# module under test
from datazen import paths


def test_unflatten_dict():
    """Test unflatten dict scenarios."""

    assert paths.unflatten_dict({"a.b.c": "test"}) == {
        "a": {"b": {"c": "test"}}
    }

    data: dict = {0: "a", "0": {"a.b.c": "test"}, "1": [{"a.b.c": "test"}]}
    expect = {
        0: "a",
        "0": {"a": {"b": {"c": "test"}}},
        "1": [{"a": {"b": {"c": "test"}}}],
    }
    assert paths.unflatten_dict(data) == expect


def test_format_resolve_delims():
    """Test custom format-String resolution."""

    assert paths.format_resolve_delims("test", {}) == "test"
    assert paths.format_resolve_delims("{a}", {"a": 5}) == "5"
    assert paths.format_resolve_delims("a{a}a", {"a": 5}) == "a5a"
    assert paths.format_resolve_delims("a{a.b.c}a", {"a.b.c": 5}) == "a5a"
