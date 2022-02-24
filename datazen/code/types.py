"""
datazen - Common type definitions for encoding and decoding interfaces.
"""

# built-in
from enum import Enum
from io import StringIO
from logging import Logger
from pathlib import Path
from typing import (
    Callable,
    FrozenSet,
    Iterator,
    NamedTuple,
    Optional,
    TextIO,
    Tuple,
    Union,
)

# third-party
from ruamel.yaml import YAML

# internal
from datazen.paths import get_file_ext


class FileExtension(Enum):
    """A mapping of expected encoding type to file extensions."""

    UNKNOWN: FrozenSet[str] = frozenset()
    JSON: FrozenSet[str] = frozenset(["json"])
    YAML: FrozenSet[str] = frozenset(["yaml", "yml", "eyaml"])
    INI: FrozenSet[str] = frozenset(["ini", "cfg"])
    ZIP: FrozenSet[str] = frozenset(["zip"])
    TAR: FrozenSet[str] = frozenset(
        ["tar", "tar.gz", "tar.bz2", "tar.lzma", "tar.xz"]
    )

    def is_archive(self) -> bool:
        """Determine if this extension is a kind of archive file."""
        return self in {FileExtension.ZIP, FileExtension.TAR}

    @staticmethod
    def has_archive(path: Path) -> Optional[Path]:
        """Determine if a path has an associated archive file."""

        for ext in [FileExtension.ZIP, FileExtension.TAR]:
            for ext_str in list(ext.value):
                check_path = Path(f"{path}.{ext_str}")
                if check_path.is_file():
                    return check_path

        return None

    def is_data(self) -> bool:
        """Determine if this etension is a kind of data file."""
        return self in {
            FileExtension.JSON,
            FileExtension.YAML,
            FileExtension.INI,
        }

    @staticmethod
    def from_ext(ext_str: str) -> Optional["FileExtension"]:
        """Given a file extension, determine what kind of file it is."""

        result = FileExtension.UNKNOWN
        for ext in FileExtension:
            if ext_str in ext.value:
                result = ext
                break
        return None if result is FileExtension.UNKNOWN else result

    @staticmethod
    def from_path(
        path: Union[Path, str], maxsplit: int = 1
    ) -> Optional["FileExtension"]:
        """Get a known file extension for a path, if it exists."""
        return FileExtension.from_ext(get_file_ext(path, maxsplit=maxsplit))

    def candidates(self, path: Path) -> Iterator[Path]:
        """
        For a given path, iterate over candidate paths that have the suffixes
        for this kind of file extension.
        """
        for ext in list(self.value):
            yield path.with_suffix(f".{ext}")


class LoadResult(NamedTuple):
    """
    An encapsulation of the result of loading raw data, the data collected and
    whether or not it succeeded.
    """

    data: dict
    success: bool
    time_ns: int = -1

    def __eq__(self, other: object) -> bool:
        """Don't compare timing when checking equivalence."""
        assert isinstance(other, (LoadResult, tuple))
        return self.data == other[0] and self.success == other[1]

    def require_success(self, path: Union[Path, str]) -> None:
        """Raise a canonical exception if this result is a failure."""
        assert self.success, f"Couldn't load '{path}'!"


EncodeResult = Tuple[bool, int]
DataStream = Union[TextIO, StringIO]
DataDecoder = Callable[[DataStream, Logger], LoadResult]
DataEncoder = Callable[[dict, DataStream, Logger], int]

# Only create the interface one so it's not re-created on every read and write
# attempt.
YAML_INTERFACE = YAML(typ="safe")
