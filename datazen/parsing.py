
"""
datazen - APIs for loading raw data from files.
"""

# built-in
import io
import json
import logging
from typing import TextIO, List

# third-party
import jinja2
from ruamel import yaml  # type: ignore

# internal
from datazen.paths import get_file_ext

LOG = logging.getLogger(__name__)


def get_json_data(data_file: TextIO) -> dict:
    """ Load JSON data from a text stream. """

    data = {}
    try:
        data = json.load(data_file)
        if not data:
            data = {}
    except json.decoder.JSONDecodeError as exc:
        LOG.error("json-load error: %s", exc)
    return data


def get_yaml_data(data_file: TextIO) -> dict:
    """ Load YAML data from a text stream. """

    data = {}
    try:
        data = yaml.safe_load(data_file)
        if not data:
            data = {}
    except (yaml.scanner.ScannerError, yaml.parser.ParserError) as exc:
        LOG.error("yaml-load error: %s", exc)
    return data


def load_stream(data_stream: TextIO, data_path: str) -> dict:
    """
    Load arbitrary data from a text stream, update an existing dictionary.
    """

    # update the dictionary
    ext = get_file_ext(data_path)
    data = {}
    if ext == "json":
        data = get_json_data(data_stream)
    elif ext == "yaml":
        data = get_yaml_data(data_stream)
    else:
        LOG.error("can't load data from '%s' (unknown extension '%s')",
                  data_path, ext)

    return data


def merge(dict_a: dict, dict_b: dict, path: List[str] = None) -> dict:
    """ TODO """

    if path is None:
        path = []

    for key in dict_b:
        if key in dict_a:
            # same leaf value
            if dict_a[key] == dict_b[key]:
                pass
            elif isinstance(dict_a[key], dict) and isinstance(dict_b[key],
                                                              dict):
                merge(dict_a[key], dict_b[key], path + [str(key)])
            elif isinstance(dict_a[key], list) and isinstance(dict_b[key],
                                                              list):
                dict_a[key].extend(dict_b[key])
            else:
                error_str = 'Conflict at %s' % '.'.join(path + [str(key)])
                LOG.error(error_str)
                LOG.error("left:  %s", dict_a[key])
                LOG.error("right: %s", dict_b[key])
        else:
            dict_a[key] = dict_b[key]

    return dict_a


def load(data_path: str, variables: dict, dict_to_update: dict) -> dict:
    """
    Load raw file data and meld it into an existing dictionary. Update
    the result as if it's a template using the provided variables.
    """

    # read the raw file and interpret it as a template, resolve 'variables'
    with open(data_path) as config_file:
        template = jinja2.Template(config_file.read())
        output = io.StringIO(template.render(variables))

    return merge(dict_to_update, load_stream(output, data_path))
