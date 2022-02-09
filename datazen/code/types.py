"""
datazen - Common type definitions for encoding and decoding interfaces.
"""

# built-in
from io import StringIO
from logging import Logger
from typing import Callable, NamedTuple, TextIO, Union


class LoadResult(NamedTuple):
    """
    An encapsulation of the result of loading raw data, the data collected and
    whether or not it succeeded.
    """

    data: dict
    success: bool


DataStream = Union[TextIO, StringIO]
DataDecoder = Callable[[DataStream, Logger], LoadResult]
DataEncoder = Callable[[dict, DataStream], None]
