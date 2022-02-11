"""
datazen - A module exposing data-file encoders and decoders.
"""

# built-in
from enum import Enum
import logging
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

# internal
from datazen.code.decode import decode_ini, decode_json, decode_yaml
from datazen.code.encode import encode_ini, encode_json, encode_yaml
from datazen.code.types import DataDecoder, DataEncoder, DataStream, LoadResult
from datazen.paths import get_file_ext


class DataHandle(NamedTuple):
    """A description of a data type."""

    extensions: List[str]
    decoder: DataDecoder
    encoder: DataEncoder


class DataType(Enum):
    """An aggregation of all known data types."""

    JSON = DataHandle(["json"], decode_json, encode_json)
    YAML = DataHandle(["yml", "yaml", "eyaml"], decode_yaml, encode_yaml)
    INI = DataHandle(["ini", "cfg"], decode_ini, encode_ini)


LOG = logging.getLogger(__name__)


class DataArbiter:
    """
    A class for looking up encode and decode functions for given data types.
    """

    def __init__(
        self, logger: logging.Logger = LOG, encoding: str = "utf-8"
    ) -> None:
        """Initialize a new data arbiter."""

        self.encoders: Dict[DataType, DataEncoder] = {}
        self.decoders: Dict[DataType, DataDecoder] = {}
        self.ext_map: Dict[str, DataType] = {}
        self.logger = logger
        self.encoding = encoding
        for dtype in DataType:
            self.encoders[dtype] = dtype.value.encoder
            self.decoders[dtype] = dtype.value.decoder
            for ext in dtype.value.extensions:
                self.ext_map[ext] = dtype

    def decoder(self, ext: str) -> Optional[DataDecoder]:
        """Look up a decoding routine from a file extension."""

        result = None
        if ext in self.ext_map:
            result = self.decoders[self.ext_map[ext]]
        else:
            self.logger.warning("No decoder for '%s'.", ext)
        return result

    def decode_stream(
        self, ext: str, stream: DataStream, logger: logging.Logger = None
    ) -> LoadResult:
        """Attempt to load data from a text stream."""

        if logger is None:
            logger = self.logger

        result = LoadResult({}, False)
        decoder = self.decoder(ext)
        if decoder is not None:
            result = decoder(stream, logger)
        return result

    def decode(self, path: Path, logger: logging.Logger = None) -> LoadResult:
        """Attempt to load data from a file."""

        result = LoadResult({}, False)
        if logger is None:
            logger = self.logger

        if path.is_file():
            with path.open(encoding=self.encoding) as path_fd:
                result = self.decode_stream(
                    get_file_ext(path), path_fd, logger
                )

        if not result.success:
            logger.error("Failed to decode '%s'.", path)

        return result

    def encode_stream(
        self,
        ext: str,
        stream: DataStream,
        data: dict,
        _: logging.Logger = None,
    ) -> bool:
        """Serialize data to an output stream."""

        result = False
        encoder = self.encoder(ext)
        if encoder is not None:
            encoder(data, stream)
            result = True
        return result

    def encode(
        self, path: Path, data: dict, logger: logging.Logger = None
    ) -> bool:
        """Encode data to a file on disk."""

        with path.open("w", encoding=self.encoding) as path_fd:
            return self.encode_stream(
                get_file_ext(path), path_fd, data, logger
            )

    def encoder(self, ext: str) -> Optional[DataEncoder]:
        """Look up an encoding routine from a file extension."""

        result = None
        if ext in self.ext_map:
            result = self.encoders[self.ext_map[ext]]
        else:
            self.logger.warning("No encoder for '%s'.", ext)
        return result


ARBITER = DataArbiter()
