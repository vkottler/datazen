"""
datazen - An interface for turning a dictionary into various serialized forms.
"""

# built-in
from io import StringIO
import logging
import os
from pathlib import Path
from typing import Tuple

# third-party
from vcorelib.dict import GenericStrDict
from vcorelib.io import ARBITER
from vcorelib.paths import Pathlike, normalize

# internal
from datazen import DEFAULT_TYPE

LOG = logging.getLogger(__name__)


def write_dir(
    directory: Pathlike, data: GenericStrDict, out_type: str = "json", **kwargs
) -> None:
    """Write dictionary data to the file-system."""

    directory = str(normalize(directory))
    os.makedirs(directory, exist_ok=True)

    for key, val in data.items():
        ARBITER.encode(Path(directory, f"{key}.{out_type}"), val, **kwargs)


def str_compile(
    configs: GenericStrDict,
    data_type: str,
    logger: logging.Logger = LOG,
    **kwargs,
) -> str:
    """
    Serialize dictionary data into the String-form of a specific,
    serializeable type.
    """

    with StringIO() as ostream:
        if ARBITER.encode_stream(
            data_type, ostream, configs, logger, **kwargs
        )[0]:
            return ostream.getvalue()
    return ""


def get_compile_output(
    entry: GenericStrDict, default_type: str = DEFAULT_TYPE
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
