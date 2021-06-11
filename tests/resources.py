
"""
datazen - An interface for retrieving and interacting with test data.
"""

# built-in
from contextlib import contextmanager
import os
from tempfile import NamedTemporaryFile
from typing import List, TextIO, Iterator
import pkg_resources

# module under test
from datazen.classes.environment import Environment, from_manifest


def get_resource(resource_name: str, valid: bool) -> str:
    """ Locate the path to a test resource. """

    valid_str = "valid" if valid else "invalid"
    resource_path = os.path.join("data", valid_str, resource_name)
    return pkg_resources.resource_filename(__name__, resource_path)


@contextmanager
def scoped_environment(resource_name: str,
                       valid: bool) -> Iterator[Environment]:
    """
    Provide an environment that's guaranteed to be instantiated with a clean
    cache, and will clean the cache again on exit.
    """

    env = from_manifest(get_resource(resource_name, valid))
    env.clean_cache()
    env = from_manifest(get_resource(resource_name, valid))
    try:
        yield env
    finally:
        env.clean_cache()


@contextmanager
def injected_content(resource_name: str, valid: bool) -> Iterator[TextIO]:
    """
    Provide a test resource as a context manager such that the original
    contents are preserved on exit.
    """

    path = get_resource(resource_name, valid)
    with open(path) as resource:
        contents = resource.read()

    try:
        with open(path, "w") as resource:
            yield resource
    finally:
        with open(path, "w") as resource:
            resource.write(contents)


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


def get_tempfile(extension: str) -> str:
    """ Obtain a temporary file name with a specific extension. """

    with NamedTemporaryFile(suffix=extension) as tfile:
        return tfile.name
