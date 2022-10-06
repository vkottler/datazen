"""
datazen - An interface for retrieving and interacting with test data.
"""

# built-in
from contextlib import contextmanager, suppress
import os
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Iterator, List, TextIO

# third-party
from git import Repo  # type: ignore
import pkg_resources

# module under test
from datazen.environment.integrated import Environment, from_manifest


def get_resource(
    resource_name: str, valid: bool = True, pkg: str = __name__
) -> str:
    """Locate the path to a test resource."""

    valid_str = "valid" if valid else "invalid"
    resource_path = os.path.join("data", valid_str, resource_name)
    return pkg_resources.resource_filename(pkg, resource_path)


def get_archives_root(pkg: str = __name__) -> Path:
    """Get the data directory for test archives."""
    resource = os.path.join("data", "archives")
    return Path(pkg_resources.resource_filename(pkg, resource))


def get_scenario_manifest(
    scenario: str, manifest: str = "manifest.yaml", pkg: str = __name__
) -> Path:
    """Get the path to a manifest in a given test scenario."""

    resource = os.path.join("data", "scenarios", scenario, manifest)
    return Path(pkg_resources.resource_filename(pkg, resource))


@contextmanager
def scoped_manifest(manifest: Path) -> Iterator[Environment]:
    """
    Provide an environment that's guaranteed to be instantiated with a clean
    cache, and will clean the cache again on exit.
    """

    env = from_manifest(str(manifest))
    env.clean_cache()
    env = from_manifest(str(manifest))
    try:
        yield env
    finally:
        env.clean_cache()


@contextmanager
def scoped_scenario(scenario: str) -> Iterator[Environment]:
    """Another scoped-manifest interface."""

    with scoped_manifest(get_scenario_manifest(scenario)) as manifest:
        yield manifest


@contextmanager
def scoped_environment(
    resource_name: str = "manifest.yaml", valid: bool = True
) -> Iterator[Environment]:
    """Another scoped-manifest interface."""

    with scoped_manifest(Path(get_resource(resource_name, valid))) as manifest:
        yield manifest


@contextmanager
def injected_content(
    resource_name: str, valid: bool = True
) -> Iterator[TextIO]:
    """
    Provide a test resource as a context manager such that the original
    contents are preserved on exit.
    """

    path = get_resource(resource_name, valid)
    with open(path, encoding="utf-8") as resource:
        contents = resource.read()

    try:
        with open(path, "w", encoding="utf-8") as resource:
            yield resource
    finally:
        with open(path, "w", encoding="utf-8") as resource:
            resource.write(contents)


def get_test_configs(valid: bool = True) -> List[str]:
    """Locate test-configuration-data root."""

    return [get_resource("configs", valid)]


def get_test_schemas(valid: bool = True) -> List[str]:
    """Locate test-schema root."""

    return [get_resource("schemas", valid)]


def get_test_templates(valid: bool = True) -> List[str]:
    """Locate test-template root."""

    return [get_resource("templates", valid)]


def get_test_variables(valid: bool = True) -> List[str]:
    """Locate test-variables root."""

    return [get_resource("variables", valid)]


@contextmanager
def get_tempfile(extension: str) -> Iterator[str]:
    """Obtain a temporary file name with a specific extension."""

    with NamedTemporaryFile(suffix=extension) as tfile:
        name = tfile.name
    yield name
    with suppress(FileNotFoundError):
        os.unlink(tfile.name)


@contextmanager
def get_temp_repo() -> Iterator[str]:
    """
    Creates a temporary directory and initializes an empty git repository.
    """

    with TemporaryDirectory() as tmpdir:
        Repo.init(tmpdir)
        yield tmpdir
