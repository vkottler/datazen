"""
datazen - Test the 'code.cache' module.
"""

# built-in
from pathlib import Path
from tempfile import TemporaryDirectory

# module under test
from datazen.code.cache import FlatDirectoryCache

# internal
from tests.resources import get_resource


def test_directory_cache_basic():
    """Test basic loading and saving functions of the directory cache."""

    # Load data.
    cache = FlatDirectoryCache(Path(get_resource("variables")))
    assert cache
    assert all(x in cache for x in "abcdef")

    # Save data, verify saved data on subsequent load.
    with TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        cache.save(tmpdir)
        new_cache = FlatDirectoryCache(tmpdir)
        assert new_cache == cache
        new_cache.save()
        assert new_cache == new_cache.load()
