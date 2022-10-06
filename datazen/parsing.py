"""
datazen - APIs for loading raw data from files.
"""

# built-in
from contextlib import ExitStack
from io import StringIO
import logging
import time

# third-party
import jinja2
from vcorelib.dict import GenericDict, GenericStrDict, merge
from vcorelib.io import ARBITER
from vcorelib.io.types import DataStream, LoadResult, StreamProcessor
from vcorelib.paths import Pathlike, file_md5_hex, normalize

LOG = logging.getLogger(__name__)


def dedup_dict_lists(data: GenericDict) -> GenericDict:
    """
    Finds list elements in a dictionary and removes duplicate entries, mutates
    the original list.
    """

    for key in data:
        if isinstance(data[key], dict):
            data[key] = dedup_dict_lists(data[key])
        elif isinstance(data[key], list):
            new_list = []
            for item in data[key]:
                if item not in new_list:
                    new_list.append(item)
            data[key] = new_list

    return data


def template_preprocessor_factory(
    variables: GenericStrDict, is_template: bool, stack: ExitStack
) -> StreamProcessor:
    """Create a stream-processing function for data decoding."""

    def processor(stream: DataStream) -> DataStream:
        """
        If the stream should be interpreted as a template, load and render it,
        returning a readable stream as a result. Otherwise return the original
        stream.
        """

        if variables and is_template:
            template = jinja2.Template(stream.read())
            stream = stack.enter_context(StringIO(template.render(variables)))

        return stream

    return processor


def load(
    path: Pathlike,
    variables: GenericStrDict,
    dict_to_update: GenericStrDict,
    expect_overwrite: bool = False,
    is_template: bool = True,
    logger: logging.Logger = LOG,
    **kwargs,
) -> LoadResult:
    """
    Load raw file data and meld it into an existing dictionary. Update
    the result as if it's a template using the provided variables.
    """

    result = LoadResult({}, False)

    with ExitStack() as stack:
        try:
            load_result = ARBITER.decode(
                path,
                logger,
                preprocessor=template_preprocessor_factory(
                    variables, is_template, stack
                ),
                **kwargs,
            )
        except jinja2.exceptions.TemplateError as exc:
            logger.error(
                "couldn't render '%s': %s (variables: %s)",
                path,
                exc,
                variables,
            )
            return result

    return LoadResult(
        merge(
            dict_to_update, load_result.data, expect_overwrite=expect_overwrite
        ),
        load_result.success,
        load_result.time_ns,
    )


def set_file_hash(
    hashes: GenericStrDict, path: Pathlike, set_new: bool = True
) -> bool:
    """Evaluate a hash dictionary and update it on a miss."""

    path = str(normalize(path))
    str_hash = file_md5_hex(path)
    result = True
    if path in hashes and str_hash == hashes[path]["hash"]:
        result = False
    elif set_new:
        if path not in hashes:
            hashes[path] = {}
        hashes[path]["hash"] = str_hash
        hashes[path]["time"] = time.time()

    return result
