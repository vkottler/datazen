"""
datazen - A module exposing data-file encoders and decoders.
"""

# built-in
from enum import Enum
from io import StringIO
from logging import Logger
from typing import Callable, Dict, List, NamedTuple, TextIO, Optional

# internal
from datazen.code.decode import (
    LoadResult,
    decode_json,
    decode_yaml,
    decode_ini,
)
from datazen.code.encode import (
    encode_json,
    encode_yaml,
    encode_ini,
)


DataDecoder = Callable[[TextIO, Logger], LoadResult]
DataEncoder = Callable[[dict, StringIO], None]


class DataHandle(NamedTuple):
    """A description of a data type."""

    extensions: List[str]
    decoder: DataDecoder
    encoder: DataEncoder


class DataType(Enum):
    """An aggregation of all known data types."""

    JSON = DataHandle(["json"], decode_json, encode_json)
    YAML = DataHandle(["yml", "yaml"], decode_yaml, encode_yaml)
    INI = DataHandle(["ini", "cfg"], decode_ini, encode_ini)


class DataArbiter:
    """
    A class for looking up encode and decode functions for given data types.
    """

    def __init__(self) -> None:
        """Initialize a new data arbiter."""

        self.encode: Dict[DataType, DataEncoder] = {}
        self.decode: Dict[DataType, DataDecoder] = {}
        self.ext_map: Dict[str, DataType] = {}
        for dtype in DataType:
            self.encode[dtype] = dtype.value.encoder
            self.decode[dtype] = dtype.value.decoder
            for ext in dtype.value.extensions:
                self.ext_map[ext] = dtype

    def decoder(self, ext: str) -> Optional[DataDecoder]:
        """Look up a decoding routine from a file extension."""

        result = None
        if ext in self.ext_map:
            result = self.decode[self.ext_map[ext]]
        return result

    def encoder(self, ext: str) -> Optional[DataEncoder]:
        """Look up an encoding routine from a file extension."""

        result = None
        if ext in self.ext_map:
            result = self.encode[self.ext_map[ext]]
        return result


ARBITER = DataArbiter()
