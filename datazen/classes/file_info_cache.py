
"""
datazen - A class for storing metadata about files that have been loaded.
"""

# built-in
from copy import deepcopy
from collections import defaultdict
import logging
import os
import shutil
from typing import Dict, List, Tuple

# internal
from datazen import DEFAULT_TYPE
from datazen.load import load_dir_only
from datazen.compile import str_compile

LOG = logging.getLogger(__name__)
DATA_DEFAULT = {"hashes": defaultdict(dict), "loaded": defaultdict(list)}


class FileInfoCache:
    """ Provides storage for file hashes and lists that have been loaded. """

    def __init__(self, cache_dir: str = None):
        """ Construct an empty cache or optionally load from a directory. """

        self.data: dict = DATA_DEFAULT
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

    def get_hashes(self, sub_dir: str) -> Dict[str, str]:
        """ Get the cached, dictionary of file hashes for a certain key. """

        return self.data["hashes"][sub_dir]

    def get_loaded(self, sub_dir: str) -> List[str]:
        """ Get the cached, list of loaded files for a certain key. """

        return self.data["loaded"][sub_dir]

    def get_data(self, name: str) -> Tuple[List[str], Dict[str, str]]:
        """ Get the tuple version of cached data. """

        return (self.get_loaded(name), self.get_hashes(name))

    def clean(self) -> None:
        """ Remove cached data from the file-system. """

        self.data = DATA_DEFAULT
        if self.cache_dir != "":
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            LOG.info("cleaning cache at '%s'", self.cache_dir)

    def write(self) -> None:
        """ Commit cached data to the file-system. """

        if self.cache_dir != "":
            for key, val in self.data.items():
                key_path = os.path.join(self.cache_dir,
                                        "{}.{}".format(key, DEFAULT_TYPE))
                key_data = str_compile(val, DEFAULT_TYPE)
                with open(key_path, "w") as key_file:
                    key_file.write(key_data)
            LOG.info("wrote cache to '%s'", self.cache_dir)


def copy(cache: FileInfoCache) -> FileInfoCache:
    """ Copy one cache into a new one. """

    new_cache = FileInfoCache()

    # copy the cache
    new_cache.cache_dir = cache.cache_dir
    new_cache.data = deepcopy(cache.data)

    return new_cache
