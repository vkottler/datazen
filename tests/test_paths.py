"""
datazen - Tests for the 'paths' API.
"""

# module under test
from datazen import paths
from datazen.code import FileExtension


def test_unflatten_dict():
    """Test unflatten dict scenarios."""

    assert paths.unflatten_dict({"a.b.c": "test"}) == {
        "a": {"b": {"c": "test"}}
    }

    data = {0: "a", "0": {"a.b.c": "test"}, "1": [{"a.b.c": "test"}]}
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


def test_file_name_ext():
    """Test various file name to extention conversions."""

    assert FileExtension.from_path("test") is None

    assert FileExtension.from_path("json") is FileExtension.JSON
    assert FileExtension.from_path("a.json") is FileExtension.JSON
    assert FileExtension.from_path("a.b.json") is not FileExtension.JSON
    assert FileExtension.from_path("a.json").is_data()

    assert FileExtension.from_path("a.tar") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.gz") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.bz2") is FileExtension.TAR
    assert FileExtension.from_path("a.tar.gz").is_archive()
