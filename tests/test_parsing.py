"""
datazen - Test functions in the 'parsing' module.
"""

# built-in
import os
from pathlib import Path

# third-party
from pytest import raises
from vcorelib.io import ARBITER

# module under test
from datazen.parsing import load

# internal
from .resources import get_resource


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
