"""
datazen - An interface for turning a dictionary into various serialized forms.
"""

# built-in
from io import StringIO
import logging
import os
from pathlib import Path
from typing import Tuple, Union

# internal
from datazen import DEFAULT_TYPE
from datazen.code import ARBITER
from datazen.code.types import DataStream

LOG = logging.getLogger(__name__)


def write_dir(
    directory: Union[Path, str], data: dict, out_type: str = "json"
) -> None:
    """Write dictionary data to the file-system."""

    directory = str(directory)
    os.makedirs(directory, exist_ok=True)
    for key, val in data.items():
        key_path = os.path.join(directory, f"{key}.{out_type}")
        with open(key_path, "w", encoding="utf-8") as key_file:
            key_file.write(str_compile(val, out_type))


def stream_compile(
    stream: DataStream,
    configs: dict,
    data_type: str,
    logger: logging.Logger = LOG,
) -> None:
    """Compile configuration data to an output stream of a specified type."""

    encoder = ARBITER.encoder(data_type)
    if encoder is None:
        logger.error("can't serialize '%s' data (unknown type)", data_type)
    else:
        encoder(configs, stream)


def str_compile(
    configs: dict, data_type: str, logger: logging.Logger = LOG
) -> str:
    """
    Serialize dictionary data into the String-form of a specific,
    serializeable type.
    """

    with StringIO() as ostream:
        stream_compile(ostream, configs, data_type, logger)
        return ostream.getvalue()


def get_compile_output(
    entry: dict, default_type: str = DEFAULT_TYPE
) -> Tuple[str, str]:
    """
    Determine the output path and type of a compile target, from the target's
    data.
    """

    # determine the output type
    output_type = entry.get("output_type", default_type)

    # write the output
    filename = entry.get("output_path", entry["name"]) + f".{output_type}"
    return os.path.join(entry["output_dir"], filename), output_type
