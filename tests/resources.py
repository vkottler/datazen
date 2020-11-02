
"""
datazen - An interface for retrieving and interacting with test data.
"""

# built-in
import os
from tempfile import NamedTemporaryFile
from typing import List, IO
import pkg_resources


def get_resource(resource_name: str, valid: bool) -> str:
    """ Locate the path to a test resource. """

    valid_str = "valid" if valid else "invalid"
    resource_path = os.path.join("data", valid_str, resource_name)
    return pkg_resources.resource_filename(__name__, resource_path)


def get_test_configs(valid: bool = True) -> List[str]:
    """ Locate test-configuration-data root. """

    return [get_resource("configs", valid)]


def get_test_schemas(valid: bool = True) -> List[str]:
    """ Locate test-schema root. """

    return [get_resource("schemas", valid)]


def get_test_templates(valid: bool = True) -> List[str]:
    """ Locate test-template root. """

    return [get_resource("templates", valid)]


def get_test_variables(valid: bool = True) -> List[str]:
    """ Locate test-variables root. """

    return [get_resource("variables", valid)]


def get_tempfile(extension: str) -> IO:
    """ Obtain a temporary file name with a specific extension. """

    return NamedTemporaryFile(suffix=extension)
