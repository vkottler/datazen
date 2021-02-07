
"""
datazen - Test functions in the 'parsing' module.
"""

# module under test
from datazen.parsing import merge


def test_bad_overwrite():
    """ Test that if we don't want to overwrite, we don't. """

    dict_a = {"a": "a"}
    dict_b = {"a": "b"}
    assert merge(dict_a, dict_b) == dict_a
    assert merge(dict_a, dict_b, expect_overwrite=True) == dict_b
