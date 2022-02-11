"""
datazen - A module for cache implementations, conforming to package-wide,
          data-structure constraints and assumptions.
"""

# built-in
from collections import UserDict
from pathlib import Path
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
    ) -> None:
        """Initialize this data cache."""

        super().__init__(initialdata)
        self.root = root
        self.encoding = encoding
        self.arbiter = arbiter
        merge(self.data, self.load(self.root))

    def load(self, path: Path = None) -> Dict[str, dict]:
        """Load data from disk."""

        if path is None:
            path = self.root

        result = {}
        if path.is_dir():
            for child in path.iterdir():
                # Don't traverse directories.
                if child.is_file():
                    load = self.arbiter.decode(child)
                    key = get_file_name(child)
                    assert key
                    if load.success:
                        assert (
                            key not in result
                        ), f"Data for '{key}' is already loaded!"
                        result[key] = load.data
        return result

    def save(self, path: Path = None) -> None:
        """Save data to disk."""

        if path is None:
            path = self.root

        path.mkdir(parents=True, exist_ok=True)
        for key, val in self.data.items():
            self.arbiter.encode(Path(path, f"{key}.{self.encoding}"), val)
