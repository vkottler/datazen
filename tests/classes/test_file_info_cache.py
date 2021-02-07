
"""
datazen - Tests for the file-info class.
"""

# built-in
from tempfile import TemporaryDirectory

# module under test
from datazen.classes.file_info_cache import FileInfoCache, meld, copy


def test_cache_meld():
    """ Test some of the more niche melding behavior of caches. """

    with TemporaryDirectory() as tdir:
        cache_b = FileInfoCache(tdir)
        hashes = cache_b.get_hashes("test")
        loaded = cache_b.get_loaded("test")

        # add some initial files
        time = 0
        for _ in range(10):
            fname = "file_{}".format(time)
            loaded.append(fname)
            hashes[fname] = {"hash": time, "time": time}
            time += 1

        cache_a = copy(cache_b)

        # add some new files
        for _ in range(5):
            fname = "file_{}".format(time)
            loaded.append(fname)
            hashes[fname] = {"hash": time, "time": time}
            time += 1

        # update some existing files
        for i in range(5):
            fname = "file_{}".format(i)
            hashes[fname] = {"hash": time, "time": time}
            time += 1

        meld(cache_a, cache_b)
