
"""
datazen - Test functions in the 'parsing' module.
"""

# built-in
import os

# module under test
from datazen.parsing import merge, load

# internal
from .resources import get_resource


def test_bad_overwrite():
    """ Test that if we don't want to overwrite, we don't. """

    dict_a = {"a": "a"}
    dict_b = {"a": "b"}
    assert merge(dict_a, dict_b) == dict_a
    assert merge(dict_a, dict_b, expect_overwrite=True) == dict_b


def test_load_bad_template():
    """ Test that loading invalid templates returns correctly. """

    template = get_resource(os.path.join("templates", "bad.j2"), False)
    assert load(template, {}, {}) == ({}, False)
