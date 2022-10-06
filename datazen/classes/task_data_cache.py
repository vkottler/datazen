"""
datazen - A class for storing data from completed operations to disk.
"""

# built-in
from collections import defaultdict
import os
import shutil

# third-party
from vcorelib.dict import GenericStrDict

# internal
from datazen.compile import write_dir
from datazen.load import load_dir_only


class TaskDataCache:
    """
    Provides storage for data produced by task targets to facilitate better
    (and more correct) short-circuiting.
    """

    def __init__(self, cache_dir: str):
        """Construct an empty cache or optionally load from a directory."""

        self.data: GenericStrDict = defaultdict(lambda: defaultdict(dict))
        self.cache_dir = cache_dir
        self.load(self.cache_dir)

    def load(self, load_dir: str) -> None:
        """Read new data from the cache directory and update state."""

        os.makedirs(load_dir, exist_ok=True)
        self.data.update(load_dir_only(load_dir, are_templates=False)[0])

    def save(self, out_type: str = "json") -> None:
        """Write cache data to disk."""

        write_dir(self.cache_dir, self.data, out_type, indent=None)

    def clean(self, purge_data: bool = True) -> None:
        """Clean this cache's data on disk."""

        shutil.rmtree(self.cache_dir)
        if purge_data:
            self.data = defaultdict(lambda: defaultdict(dict))
