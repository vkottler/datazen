"""
datazen - Common type definitions for encoding and decoding interfaces.
"""

# built-in
from io import StringIO
from logging import Logger
from typing import Callable, NamedTuple, TextIO, Tuple, Union

# third-party
from ruamel.yaml import YAML


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


EncodeResult = Tuple[bool, int]
DataStream = Union[TextIO, StringIO]
DataDecoder = Callable[[DataStream, Logger], LoadResult]
DataEncoder = Callable[[dict, DataStream, Logger], int]

# Only create the interface one so it's not re-created on every read and write
# attempt.
YAML_INTERFACE = YAML(typ="safe")
