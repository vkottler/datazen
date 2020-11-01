
"""
datazen - An interface for retrieving and interacting with test data.
"""

# built-in
import os
import pkg_resources


def get_resource(resource_name: str, valid: bool) -> str:
    """ Locate the path to a test resource. """

    valid = "valid" if valid else "invalid"
    resource_path = os.path.join("data", valid, resource_name)
    return pkg_resources.resource_filename(__name__, resource_path)


def get_test_configs(valid: bool = True) -> str:
    """ Locate test-configuration-data root. """

    return get_resource("configs", valid)


def get_test_schemas(valid: bool = True) -> str:
    """ Locate test-schema root. """

    return get_resource("schemas", valid)


def get_test_templates(valid: bool = True) -> str:
    """ Locate test-template root. """

    return get_resource("templates", valid)


def get_test_variables(valid: bool = True) -> str:
    """ Locate test-variables root. """

    return get_resource("variables", valid)
