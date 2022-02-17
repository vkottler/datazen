"""
datazen - A module for cache implementations, conforming to package-wide,
          data-structure constraints and assumptions.
"""

# built-in
from collections import UserDict
from pathlib import Path
from time import time_ns
from typing import Dict

# internal
from datazen.code import ARBITER, DataArbiter
from datazen.parsing import merge
from datazen.paths import get_file_name


class FlatDirectoryCache(UserDict):
    """
    A class implementing a dictionary that can be saved and loaded from disk,
    with a specified encoding scheme.
    """

    def __init__(
        self,
        root: Path,
        initialdata: dict = None,
        encoding: str = "json",
        arbiter: DataArbiter = ARBITER,
        **load_kwargs,
    ) -> None:
        """Initialize this data cache."""

        super().__init__(initialdata)
        self.root = root
        self.encoding = encoding
        self.arbiter = arbiter
        self.load_time_ns: int = -1
        self.save_time_ns: int = -1
        merge(self.data, self.load(self.root, **load_kwargs))

    def load(self, path: Path = None, **kwargs) -> Dict[str, dict]:
        """Load data from disk."""

        if path is None:
            path = self.root

        result = {}
        if path.is_dir():
            start = time_ns()
            for child in path.iterdir():
                # Don't traverse directories.
                if child.is_file():
                    load = self.arbiter.decode(child, **kwargs)
                    key = get_file_name(child)
                    assert key
                    if load.success:
                        assert (
                            key not in result
                        ), f"Data for '{key}' is already loaded!"
                        result[key] = load.data

            # Update load time.
            self.load_time_ns = time_ns() - start
        return result

    def save(self, path: Path = None, **kwargs) -> None:
        """Save data to disk."""

        if path is None:
            path = self.root

        start = time_ns()
        path.mkdir(parents=True, exist_ok=True)
        for key, val in self.data.items():
            assert self.arbiter.encode(
                Path(path, f"{key}.{self.encoding}"), val, **kwargs
            )[0], f"Couldn't write key '{key}' to cache ({path})!"

        # Update save time.
        self.save_time_ns = time_ns() - start
