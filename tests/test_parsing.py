"""
datazen - Test functions in the 'parsing' module.
"""

# built-in
import os
from pathlib import Path

# third-party
from pytest import raises

# module under test
from datazen.code import ARBITER
from datazen.parsing import (
    dict_resolve_env_vars,
    list_resolve_env_vars,
    load,
    merge,
    str_resolve_env_var,
)

# internal
from .resources import get_resource


def test_bad_overwrite():
    """Test that if we don't want to overwrite, we don't."""

    dict_a = {"a": "a"}
    dict_b = {"a": "b"}
    assert merge(dict_a, dict_b) == dict_a
    assert merge(dict_a, dict_b, expect_overwrite=True) == dict_b


def test_load_bad_template():
    """Test that loading invalid templates returns correctly."""

    template = get_resource(os.path.join("templates", "bad.j2"), False)
    assert load(template, {"a": 1}, {}) == ({}, False)


def test_load_assert():
    """Verify that requiring success on a load works."""

    bad_load = get_resource(os.path.join("variables", "bad.json"), False)
    with raises(AssertionError):
        ARBITER.decode(Path(bad_load), require_success=True)

    with raises(AssertionError):
        load(bad_load, {}, {}, require_success=True)


def test_resolve_env_vars():
    """
    Test that we can correctly resolve environment variables in data
    structures.
    """

    os.environ["TEST"] = "test"
    assert str_resolve_env_var("$TEST") == "test"
    assert list_resolve_env_vars(["$TEST", ["$TEST"], {"$TEST": "$TEST"}]) == [
        "test",
        ["test"],
        {"test": "test"},
    ]
    assert dict_resolve_env_vars({"a": {"b": ["$TEST"]}}) == {
        "a": {"b": ["test"]}
    }
