
"""
datazen - Tests for the 'Environment' class.
"""

# built-in
import os

# module under test
from datazen.classes.base_environment import DataType
from datazen.classes.environment import from_manifest

# internal
from ..environment import EnvironmentMock
from ..resources import get_test_configs, get_resource


def test_environment():
    """ Basic tests for the Environment class, wrapped by EnvironmentMock. """

    env = EnvironmentMock()
    assert env

    # load configs twice, it should also load variables
    assert env.get_configs(True)
    assert env.get_configs(True)
    assert env.get_variables(True)

    # make sure duplicates are rejected
    for config_dir in get_test_configs(True):
        assert not env.valid.add_dir(DataType.CONFIG, config_dir)

    # make sure non-directories are rejected
    assert not env.valid.add_dir(DataType.CONFIG, "/this/dir/shouldn't/exist")


def test_environment_from_manifest():
    """ TODO """

    manifest_path = get_resource(os.path.join("manifests", "test.yaml"), True)
    env = from_manifest(manifest_path)
    assert env

    manifest_path = get_resource(os.path.join("manifests", "test.yaml"), False)
    env = from_manifest(manifest_path)
    assert env
