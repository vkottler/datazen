
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
from ..resources import get_test_configs, get_resource, scoped_environment


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


def test_bad_include():
    """
    Test the behavior of loading manifests when the includes have problems.
    """

    # load an invalid manifest (bad include)
    manifest_path = get_resource(os.path.join("manifests", "bad_include.yaml"),
                                 False)
    env = from_manifest(manifest_path)
    assert not env.get_valid()
    env.clean_cache()


def test_environment_from_manifest():
    """ Test scenarios for loading manifest files. """

    # load an invalid manifest (bad schema)
    manifest_path = get_resource(os.path.join("manifests", "test.yaml"), False)
    env = from_manifest(manifest_path)
    assert not env.get_valid()

    # make sure we can't double-load the manifest
    assert not env.load_manifest_with_cache(manifest_path)

    # load an invalid manifest (bad content)
    manifest_path = get_resource(os.path.join("manifests", "invalid.yaml"),
                                 False)
    env = from_manifest(manifest_path)
    assert not env.get_valid()
    assert env.compile("a") == (False, False)
    env.clean_cache()


def test_operations():
    """ Test some 'compile' and 'render' scenarios. """

    with scoped_environment("manifest.yaml", True) as env:
        assert env.manifest_changed

        assert env.render("a") == (True, True)
        # here 'b' render is already satisfied, because a compile depended
        # on it
        assert env.render("b") == (True, False)

        # test default goals
        assert env.execute() == (True, False)
        del env.manifest["data"]["default_target"]
        assert env.execute() == (True, False)

        # test builds that should fail
        assert env.render("xx") == (False, False)
        assert env.render("z") == (False, False)
        assert env.render("c") == (False, False)
        assert env.render("d") == (False, False)
        assert env.compile("d") == (False, False)
        assert env.compile("g") == (False, False)
        assert env.render("e") == (False, False)


def test_load_manifest():
    """ Test a nominal manifest-loading scenario. """

    with scoped_environment("manifest.yaml", True) as env:
        cfg_data1 = env.cached_load_configs()
        assert cfg_data1
        assert env.cached_load_configs()
        env.write_cache()

        assert env.cached_enforce_schemas(cfg_data1)

        # clean the cache
        env.clean_cache()

        cfg_data2 = env.cached_load_configs()
        assert cfg_data2
        assert cfg_data2 == cfg_data1
        env.write_cache()

        # make sure configs loaded correctly
        assert "yaml2" in cfg_data2 and "json2" in cfg_data2
        assert len(cfg_data2["top_list"]) == 6
