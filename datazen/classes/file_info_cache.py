
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
from datazen import VERSION
from datazen.parsing import set_file_hash, merge, dedup_dict_lists
from datazen.load import load_dir_only
from datazen.compile import str_compile

LOG = logging.getLogger(__name__)

DATA_DEFAULT = {"hashes": defaultdict(lambda: defaultdict(dict)),
                "loaded": defaultdict(list),
                "meta": {"version": VERSION}}


class FileInfoCache:
    """ Provides storage for file hashes and lists that have been loaded. """

    def __init__(self, cache_dir: str = None):
        """ Construct an empty cache or optionally load from a directory. """

        self.data: dict = deepcopy(DATA_DEFAULT)
        self.removed_data: Dict[str, List[str]] = defaultdict(list)
        self.cache_dir: str = ""
        if cache_dir is not None:
            self.load(cache_dir)

    def load(self, cache_dir: str) -> None:
        """ Load data from a directory. """

        assert self.cache_dir == ""
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

        # reject things that don't belong by updating instead of assigning
        new_data = sync_cache_data(load_dir_only(self.cache_dir, True),
                                   self.removed_data)
        for key in DATA_DEFAULT:
            self.data[key].update(new_data[key])

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
            # guard against a failure in the "new" detection
            loaded_data = self.get_loaded(sub_dir)
            if abs_path not in loaded_data:
                loaded_data.append(abs_path)

        return not is_new

    def get_loaded(self, sub_dir: str) -> List[str]:
        """ Get the cached, list of loaded files for a certain key. """

        return self.data["loaded"][sub_dir]

    def describe(self) -> None:
        """ Describe this cache's contents for debugging purposes. """

        curr_dir = os.getcwd()
        for hash_set, hash_data in self.data["hashes"].items():
            misses = []
            total = len(self.removed_data[hash_set])
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
            for removed in self.removed_data[hash_set]:
                LOG.info("%s no longer present", removed)

            # log a summary
            LOG.info("%s: %d/%d match", hash_set,
                     total - (len(misses) + len(self.removed_data[hash_set])),
                     total)

        # describe metadata
        if "meta" in self.data:
            LOG.info("version: %s (current: %s)",
                     self.data["meta"]["version"], VERSION)

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
            data = sync_cache_data(self.data, self.removed_data)
            for key, val in data.items():
                key_path = os.path.join(self.cache_dir,
                                        "{}.{}".format(key, out_type))
                with open(key_path, "w") as key_file:
                    key_file.write(str_compile(val, out_type))
            LOG.debug("wrote cache to '%s'", self.cache_dir)


def copy(cache: FileInfoCache) -> FileInfoCache:
    """ Copy one cache into a new one. """

    new_cache = FileInfoCache()

    # copy the cache
    new_cache.cache_dir = cache.cache_dir
    new_cache.data = deepcopy(cache.data)
    new_cache.removed_data = deepcopy(cache.removed_data)

    return new_cache


def meld(cache_a: FileInfoCache, cache_b: FileInfoCache) -> None:
    """ Promote all updates from cache_b into cache_a. """

    merge(cache_a.data, cache_b.data, expect_overwrite=True)


def time_str(time_s: float) -> str:
    """ Concert a timestamp to a String. """

    return time.strftime("%c", time.localtime(time_s))


def cmp_loaded_count(cache_a: FileInfoCache, cache_b: FileInfoCache,
                     name: str) -> int:
    """
    Compute the total difference in file counts (for a named group)
    between two caches.
    """

    a_loaded = cache_a.get_loaded(name)
    b_loaded = cache_b.get_loaded(name)

    # get counts of all the files from both caches
    count_data: dict = defaultdict(lambda: {"a": 0, "b": 0})
    for item in a_loaded:
        count_data[item]["a"] = a_loaded.count(item)
    for item in b_loaded:
        count_data[item]["b"] = b_loaded.count(item)

    # accumulated the differences in counts
    result = 0
    for data in count_data.values():
        result += abs(data["a"] - data["b"])
    return result


def cmp_loaded_count_from_set(cache_a: FileInfoCache, cache_b: FileInfoCache,
                              name: str, files: List[str]) -> int:
    """
    Count the number of files uniquely loaded to one cache but not the other.
    """

    result = 0
    a_loaded = cache_a.get_loaded(name)
    b_loaded = cache_b.get_loaded(name)
    for filename in files:
        full_name = os.path.abspath(filename)
        if a_loaded.count(full_name) > b_loaded.count(full_name):
            result += 1
    return result


def cmp_total_loaded(cache_a: FileInfoCache, cache_b: FileInfoCache,
                     known_types: List[str],
                     load_checks: Dict[str, List[str]] = None) -> int:
    """
    Compute the total difference in file counts for a provided set of named
    groups.
    """

    result = 0
    for known in known_types:
        if load_checks is not None and known in load_checks:
            iter_result = cmp_loaded_count_from_set(cache_a, cache_b, known,
                                                    load_checks[known])
            if iter_result > 0:
                LOG.info("%d changes detected for '%s' in '%s'", iter_result,
                         known, load_checks[known])
            result += iter_result
        else:
            iter_result = cmp_loaded_count(cache_a, cache_b, known)
            if iter_result > 0:
                LOG.info("%d changes detected for '%s'", iter_result, known)
            result += iter_result
    return result


def sync_cache_data(cache_data: dict,
                    removed_data: Dict[str, List[str]]) -> dict:
    """
    Before writing a cache to disk we want to de-duplicate items in the loaded
    list and remove hash data for files that were removed so that if they
    come back at the same hash, it's not considered already loaded.
    """

    data = dedup_dict_lists(deepcopy(cache_data))
    data["hashes"] = remove_missing_hashed_files(data["hashes"], removed_data)
    data["loaded"] = remove_missing_loaded_files(data["loaded"])
    return data


def remove_missing_hashed_files(data: dict,
                                removed_data: Dict[str, List[str]]) -> dict:
    """ Assign new hash data based on the files that are still present. """

    for category in data.keys():
        new_data = {}
        for filename in data[category].keys():
            if os.path.isfile(filename):
                new_data[filename] = data[category][filename]
            elif filename not in removed_data[category]:
                removed_data[category].append(filename)
        data[category] = new_data

    return data


def remove_missing_loaded_files(data: dict) -> dict:
    """
    Audit list elements in a dictionary recursively, assume the data is String
    and the elements are filenames, assign a new list for all of the elements
    that can be located.
    """

    for key, item in data.items():
        new_list = []
        for filename in item:
            if os.path.isfile(filename):
                new_list.append(filename)
        data[key] = new_list

    return data
