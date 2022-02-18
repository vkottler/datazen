"""
datazen - A module for cache implementations, conforming to package-wide,
          data-structure constraints and assumptions.
"""

# built-in
from collections import UserDict
import logging
from pathlib import Path
from time import perf_counter_ns
from typing import Dict

# internal
from datazen.code import ARBITER, DataArbiter
from datazen.parsing import merge
from datazen.paths import get_file_name, nano_str


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

        # A derived class must add logic to set this.
        self.changed: bool = False

        merge(self.data, self.load(self.root, **load_kwargs))

    def load(
        self,
        path: Path = None,
        logger: logging.Logger = None,
        level: int = logging.DEBUG,
        **kwargs,
    ) -> Dict[str, dict]:
        """Load data from disk."""

        if path is None:
            path = self.root

        result = {}
        if path.is_dir():
            start = perf_counter_ns()
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
            self.load_time_ns = perf_counter_ns() - start
            if logger is not None:
                logger.log(
                    level, "Cache loaded in %ss.", nano_str(self.load_time_ns)
                )
        return result

    def save(
        self,
        path: Path = None,
        logger: logging.Logger = None,
        level: int = logging.DEBUG,
        **kwargs,
    ) -> None:
        """Save data to disk."""

        if path is None:
            path = self.root

        if self.changed:
            start = perf_counter_ns()
            path.mkdir(parents=True, exist_ok=True)
            for key, val in self.data.items():
                assert self.arbiter.encode(
                    Path(path, f"{key}.{self.encoding}"), val, **kwargs
                )[0], f"Couldn't write key '{key}' to cache ({path})!"

            # Update save time.
            self.save_time_ns = perf_counter_ns() - start
            if logger is not None:
                logger.log(
                    level, "Cache written in %ss.", nano_str(self.save_time_ns)
                )
            self.changed = False
