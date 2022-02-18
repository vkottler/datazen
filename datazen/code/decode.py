"""
datazen - A module implementing various data-file decoders.
"""

# built-in
from configparser import ConfigParser, Error, ExtendedInterpolation
import json
from logging import Logger, getLogger
from time import perf_counter_ns
from typing import Dict

# third-party
from ruamel.yaml import parser, scanner

# internal
from datazen.code.types import YAML_INTERFACE, DataStream, LoadResult

LOG = getLogger(__name__)
INI_INTERPOLATION = ExtendedInterpolation()


def decode_ini(
    data_file: DataStream,
    logger: Logger = LOG,
    **kwargs,
) -> LoadResult:
    """Load INI data from a text stream."""

    start = perf_counter_ns()
    data = {}
    loaded = True

    # Allow interpolation when reading by default.
    interpolation = kwargs.get("interpolation", INI_INTERPOLATION)
    try:
        del kwargs["interpolation"]
    except KeyError:
        pass

    cparser = ConfigParser(interpolation=interpolation, **kwargs)
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

    return LoadResult(data, loaded, perf_counter_ns() - start)


def decode_json(
    data_file: DataStream,
    logger: Logger = LOG,
    **kwargs,
) -> LoadResult:
    """Load JSON data from a text stream."""

    start = perf_counter_ns()
    data = {}
    loaded = True
    try:
        data = json.load(data_file, **kwargs)
        if not data:
            data = {}
    except json.decoder.JSONDecodeError as exc:
        loaded = False
        logger.error("json-load error: %s", exc)
    return LoadResult(data, loaded, perf_counter_ns() - start)


def decode_yaml(
    data_file: DataStream,
    logger: Logger = LOG,
    **kwargs,
) -> LoadResult:
    """Load YAML data from a text stream."""

    start = perf_counter_ns()
    data = {}
    loaded = True
    try:
        data = YAML_INTERFACE.load(data_file, **kwargs)
        if not data:
            data = {}
    except (scanner.ScannerError, parser.ParserError) as exc:
        loaded = False
        logger.error("yaml-load error: %s", exc)
    return LoadResult(data, loaded, perf_counter_ns() - start)
