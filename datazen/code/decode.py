"""
datazen - A module implementing various data-file decoders.
"""

# built-in
from configparser import ConfigParser, ExtendedInterpolation, Error
import json
import logging
from typing import Dict, NamedTuple, TextIO

# third-party
from ruamel.yaml import YAML, scanner, parser

LOG = logging.getLogger(__name__)
INI_INTERPOLATION = ExtendedInterpolation()


class LoadResult(NamedTuple):
    """
    An encapsulation of the result of loading raw data, the data collected and
    whether or not it succeeded.
    """

    data: dict
    success: bool


def decode_ini(
    data_file: TextIO,
    logger: logging.Logger = LOG,
) -> LoadResult:
    """Load INI data from a text stream."""

    data = {}
    loaded = True

    cparser = ConfigParser(interpolation=INI_INTERPOLATION)
    try:
        cparser.read_file(data_file)

        for sect_key, section in cparser.items():
            sect_data: Dict[str, str] = {}
            data[sect_key] = sect_data
            for key, value in section.items():
                sect_data[key] = value
    except Error as exc:
        loaded = False
        logger.error("config-load error: %s", exc)

    return LoadResult(data, loaded)


def decode_json(
    data_file: TextIO,
    logger: logging.Logger = LOG,
) -> LoadResult:
    """Load JSON data from a text stream."""

    data = {}
    loaded = True
    try:
        data = json.load(data_file)
        if not data:
            data = {}
    except json.decoder.JSONDecodeError as exc:
        loaded = False
        logger.error("json-load error: %s", exc)
    return LoadResult(data, loaded)


def decode_yaml(
    data_file: TextIO,
    logger: logging.Logger = LOG,
) -> LoadResult:
    """Load YAML data from a text stream."""

    data = {}
    loaded = True
    try:
        data = YAML(typ="safe").load(data_file)
        if not data:
            data = {}
    except (scanner.ScannerError, parser.ParserError) as exc:
        loaded = False
        logger.error("yaml-load error: %s", exc)
    return LoadResult(data, loaded)
