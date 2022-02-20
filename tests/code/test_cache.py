"""
datazen - Test the 'code.cache' module.
"""

# built-in
import logging
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

# module under test
from datazen.code.cache import FlatDirectoryCache

# internal
from tests.resources import get_archives_root, get_resource


def test_directory_cache_basic():
    """Test basic loading and saving functions of the directory cache."""

    # Load data.
    logger = logging.getLogger(__name__)
    cache = FlatDirectoryCache(Path(get_resource("variables")), logger=logger)
    cache.changed = True
    assert cache
    assert all(x in cache for x in "abcdef")

    # Save data, verify saved data on subsequent load.
    with TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        cache.save(tmpdir, logger=logger)
        new_cache = FlatDirectoryCache(tmpdir, logger=logger)
        new_cache.changed = True
        assert new_cache == cache
        new_cache.save(logger=logger)
        assert new_cache == new_cache.load()


def test_directory_cache_archive_load():
    """Test that we can load a cache, when only an archive for it exists."""

    logger = logging.getLogger(__name__)
    root = get_archives_root()
    for archive in ["tar", "tar.bz2", "tar.gz", "tar.lzma", "zip"]:
        archive_name = f"sample.{archive}"
        path = Path(root, archive_name)

        with TemporaryDirectory() as tmp:
            # Copy the archive to the expected location.
            shutil.copy(path, Path(tmp, archive_name))

            # Load the cache.
            cache = FlatDirectoryCache(Path(tmp, "sample"), logger=logger)
            assert cache
            assert all(x in cache for x in "abc")


def test_directory_cache_save_archive():
    """Test that we can create a cache archive and load from it."""

    logger = logging.getLogger(__name__)
    cache = FlatDirectoryCache(Path(get_resource("variables")), logger=logger)
    assert cache

    with TemporaryDirectory() as tmp:
        path = Path(tmp, "test")
        cache.changed = True
        cache.save(path, logger, archive=True)

        # Remove the non-archived data.
        shutil.rmtree(path)
        assert Path(tmp, f"test.{cache.archive_encoding}").is_file()

        # Create a new cache, only load from the archive.
        new_cache = FlatDirectoryCache(path, logger=logger)
        assert new_cache.data == cache.data
