
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
    """ Test scenarios for loading manifest files. """

    # load an invalid manifest (bad schema)
    manifest_path = get_resource(os.path.join("manifests", "test.yaml"), False)
    env = from_manifest(manifest_path)
    assert not env.valid

    # make sure we can't double-load the manifest
    assert not env.load_manifest_with_cache(manifest_path)

    # load an invalid manifest (bad content)
    manifest_path = get_resource(os.path.join("manifests", "invalid.yaml"),
                                 False)
    env = from_manifest(manifest_path)
    assert not env.valid


def test_load_manifest():
    """ Test a nominal manifest-loading scenario. """

    env = from_manifest(get_resource("manifest.yaml", True))
    cfg_data = env.load_configs()
    assert env.load_configs()

    # make sure configs loaded correctly
    assert "yaml2" in cfg_data and "json2" in cfg_data
    assert len(cfg_data["top_list"]) == 6

    assert env.compile("a")
    assert env.compile("b")
    assert not env.compile("c")
    assert env.render("a")
    assert env.render("b")
    assert not env.render("c")
