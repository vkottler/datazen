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


def test_nano_str():
    """Test that the nano_str method produces the correct results."""

    val = 1
    assert paths.nano_str(val) == "1n"
    val = val * 1000 + 1
    assert paths.nano_str(val) == "1.001u"
    val *= 1000
    assert paths.nano_str(val) == "1.001m"
    val *= 1000
    assert paths.nano_str(val) == "1.001"
    val *= 1000
    assert paths.nano_str(val) == "1001"

    assert paths.nano_str(val, max_prefix=4) == "1.001k"
    assert paths.nano_str(val * 1000, max_prefix=5) == "1.001M"

    # Test when the value is time.
    assert paths.seconds_str(60) == ("1m", 0)
    assert paths.seconds_str(61) == ("1m", 1)
    assert paths.seconds_str(3600) == ("1h 0m", 0)
    assert paths.seconds_str(3661) == ("1h 1m", 1)
    assert paths.nano_str(val, True) == "16m 41"


def test_byte_count_str():
    """Test that the byte_count_str method produces the correct results."""
    assert paths.byte_count_str(0) == "0 B"
    assert paths.byte_count_str(1024) == "1 KiB"
    assert paths.byte_count_str(1536) == "1.500 KiB"


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
