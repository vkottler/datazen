
"""
datazen - A class for storing metadata about files that have been loaded.
"""

# built-in
from copy import deepcopy
from collections import defaultdict
import logging
import os
import shutil
import time
from typing import Dict, List, Tuple

# internal
from datazen.parsing import set_file_hash, merge
from datazen.load import load_dir_only
from datazen.compile import str_compile

LOG = logging.getLogger(__name__)

DATA_DEFAULT = {"hashes": defaultdict(lambda: defaultdict(dict)),
                "loaded": defaultdict(list)}


class FileInfoCache:
    """ Provides storage for file hashes and lists that have been loaded. """

    def __init__(self, cache_dir: str = None):
        """ Construct an empty cache or optionally load from a directory. """

        self.data: dict = deepcopy(DATA_DEFAULT)
        self.cache_dir: str = ""
        if cache_dir is not None:
            self.load(cache_dir)

    def load(self, cache_dir: str) -> None:
        """ Load data from a directory. """

        assert self.cache_dir == ""
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

        # reject things that don't belong by updating instead of assigning
        new_data = load_dir_only(self.cache_dir)
        self.data["hashes"].update(new_data["hashes"])
        self.data["loaded"].update(new_data["loaded"])

    def get_hashes(self, sub_dir: str) -> Dict[str, dict]:
        """ Get the cached, dictionary of file hashes for a certain key. """

        return self.data["hashes"][sub_dir]

    def check_hit(self, sub_dir: str, path: str,
                  also_cache: bool = True) -> bool:
        """
        Determine if a given file already exists with its current hash in the
        cache, if not return False and optionally add it to the cache. """

        abs_path = os.path.abspath(path)
        is_new = set_file_hash(self.get_hashes(sub_dir), abs_path, also_cache)
        if also_cache and is_new:
            self.get_loaded(sub_dir).append(abs_path)

        return not is_new

    def get_loaded(self, sub_dir: str) -> List[str]:
        """ Get the cached, list of loaded files for a certain key. """

        return self.data["loaded"][sub_dir]

    def describe(self) -> None:
        """ Describe this cache's contents for debugging purposes. """

        curr_dir = os.getcwd()
        for hash_set, hash_data in self.data["hashes"].items():
            misses = []
            total = 0
            for filename, hash_item in hash_data.items():
                total += 1
                if curr_dir in filename:
                    filename = filename[len(curr_dir) + 1:]
                if not self.check_hit(hash_set, filename, False):
                    misses.append((filename, hash_item))
                else:
                    LOG.debug("%s (%s) matched", filename,
                              time_str(hash_item["time"]))

            # log all misses / updates
            for miss in misses:
                LOG.info("%s (%s) updated", miss[0], time_str(miss[1]["time"]))

            # log a summary
            LOG.info("%s: %d/%d match", hash_set, total - len(misses), total)

    def get_data(self, name: str) -> Tuple[List[str], Dict[str, dict]]:
        """ Get the tuple version of cached data. """

        return (self.get_loaded(name), self.get_hashes(name))

    def clean(self) -> None:
        """ Remove cached data from the file-system. """

        self.data = deepcopy(DATA_DEFAULT)
        if self.cache_dir != "":
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            LOG.info("cleaning cache at '%s'", self.cache_dir)

    def write(self, out_type: str = "json") -> None:
        """ Commit cached data to the file-system. """

        if self.cache_dir != "":
            for key, val in self.data.items():
                key_path = os.path.join(self.cache_dir,
                                        "{}.{}".format(key, out_type))
                with open(key_path, "w") as key_file:
                    key_file.write(str_compile(val, out_type))
            LOG.info("wrote cache to '%s'", self.cache_dir)


def copy(cache: FileInfoCache) -> FileInfoCache:
    """ Copy one cache into a new one. """

    new_cache = FileInfoCache()

    # copy the cache
    new_cache.cache_dir = cache.cache_dir
    new_cache.data = deepcopy(cache.data)

    return new_cache


def meld(cache_a: FileInfoCache, cache_b: FileInfoCache) -> None:
    """ Promote all updates from cache_b into cache_a. """

    merge(cache_a.data, cache_b.data)


def time_str(time_s: float) -> str:
    """ Concert a timestamp to a String. """

    return time.strftime("%c", time.localtime(time_s))


def cmp_loaded_count(cache_a: FileInfoCache, cache_b: FileInfoCache,
                     name: str) -> int:
    """
    Compute the total difference in file counts (for a named group)
    between two caches.
    """

    return abs(len(cache_a.get_loaded(name)) - len(cache_b.get_loaded(name)))


def cmp_total_loaded(cache_a: FileInfoCache, cache_b: FileInfoCache,
                     known_types: List[str]) -> int:
    """
    Compute the total difference in file counts for a provided set of named
    groups.
    """

    result = 0
    for known in known_types:
        result += cmp_loaded_count(cache_a, cache_b, known)
    return result
