"""
datazen - A module exposing data-file encoders and decoders.
"""

# built-in
from enum import Enum
import logging
from pathlib import Path
from typing import NamedTuple, Optional

# internal
from datazen.code.decode import decode_ini, decode_json, decode_yaml
from datazen.code.encode import encode_ini, encode_json, encode_yaml
from datazen.code.types import (
    DataDecoder,
    DataEncoder,
    DataStream,
    EncodeResult,
    FileExtension,
    LoadResult,
)
from datazen.paths import get_file_ext


class DataHandle(NamedTuple):
    """A description of a data type."""

    decoder: DataDecoder
    encoder: DataEncoder


class DataType(Enum):
    """An aggregation of all known data types."""

    INI = DataHandle(decode_ini, encode_ini)
    JSON = DataHandle(decode_json, encode_json)
    YAML = DataHandle(decode_yaml, encode_yaml)

    @staticmethod
    def from_ext(ext: FileExtension = None) -> Optional["DataType"]:
        """Map a file extension to a data type."""

        if ext is None:
            ext = FileExtension.UNKNOWN
        mapping = {
            FileExtension.INI: DataType.INI,
            FileExtension.JSON: DataType.JSON,
            FileExtension.YAML: DataType.YAML,
        }
        return mapping.get(ext)

    @staticmethod
    def from_ext_str(ext: str) -> Optional["DataType"]:
        """Get a data type from a file-extension string."""
        return DataType.from_ext(FileExtension.from_ext(ext))


LOG = logging.getLogger(__name__)


class DataArbiter:
    """
    A class for looking up encode and decode functions for given data types.
    """

    def __init__(
        self, logger: logging.Logger = LOG, encoding: str = "utf-8"
    ) -> None:
        """Initialize a new data arbiter."""
        self.logger = logger
        self.encoding = encoding

    def decoder(self, ext: str) -> Optional[DataDecoder]:
        """Look up a decoding routine from a file extension."""

        result = None
        dtype = DataType.from_ext_str(ext)
        if dtype is not None:
            result = dtype.value.decoder
        else:
            self.logger.warning("No decoder for '%s'.", ext)
        return result

    def decode_stream(
        self,
        ext: str,
        stream: DataStream,
        logger: logging.Logger = None,
        **kwargs,
    ) -> LoadResult:
        """Attempt to load data from a text stream."""

        if logger is None:
            logger = self.logger

        result = LoadResult({}, False)
        decoder = self.decoder(ext)
        if decoder is not None:
            result = decoder(stream, logger, **kwargs)
        return result

    def decode(
        self, path: Path, logger: logging.Logger = None, **kwargs
    ) -> LoadResult:
        """Attempt to load data from a file."""

        result = LoadResult({}, False)
        if logger is None:
            logger = self.logger

        if path.is_file():
            with path.open(encoding=self.encoding) as path_fd:
                result = self.decode_stream(
                    get_file_ext(path, maxsplit=1), path_fd, logger, **kwargs
                )

        if not result.success:
            logger.error("Failed to decode '%s'.", path)

        return result

    def encode_stream(
        self,
        ext: str,
        stream: DataStream,
        data: dict,
        logger: logging.Logger = None,
        **kwargs,
    ) -> EncodeResult:
        """Serialize data to an output stream."""

        if logger is None:
            logger = self.logger

        result = False
        encoder = self.encoder(ext)
        time_ns = -1
        if encoder is not None:
            time_ns = encoder(data, stream, logger, **kwargs)
            result = True
        return result, time_ns

    def encode(
        self, path: Path, data: dict, logger: logging.Logger = None, **kwargs
    ) -> EncodeResult:
        """Encode data to a file on disk."""

        with path.open("w", encoding=self.encoding) as path_fd:
            return self.encode_stream(
                get_file_ext(path, maxsplit=1), path_fd, data, logger, **kwargs
            )

    def encoder(self, ext: str) -> Optional[DataEncoder]:
        """Look up an encoding routine from a file extension."""

        result = None
        dtype = DataType.from_ext_str(ext)
        if dtype is not None:
            result = dtype.value.encoder
        else:
            self.logger.warning("No encoder for '%s'.", ext)
        return result


ARBITER = DataArbiter()
