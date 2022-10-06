"""
datazen - Test functions in the 'targets' module.
"""

# third-party
from vcorelib.target import Target

# module under test
from datazen.paths import unflatten_dict
from datazen.targets import resolve_target_data


def test_parse_target_hiera():
    """Test a pattern-matching case with delimeters in the key name."""

    matcher = Target("test-{a.b.c}-target")
    result = matcher.evaluate("test-hello-target")
    assert result.matched

    assert result.substitutions is not None
    assert unflatten_dict(result.substitutions) == {"a": {"b": {"c": "hello"}}}

    result = matcher.evaluate("test-asdf.asdf-target")
    assert result.matched


def test_parse_target_basic():
    """Test some simple pattern-matching cases."""

    matcher = Target("{test1}-{test2}")
    result = matcher.evaluate("asdf-asdf")
    target_data = {
        "a": [
            "{test1}-{test2}",
            ["{test1}-{test2}", "{test1}-{test2}"],
            {"a": "{test1}-{test2}", "b": "asdf"},
            1,
        ],
        "b": {},
        "c": {"a": [], "b": "{test1}", "c": "{test2}"},
        "d": "{test1}-{test2}",
        "e": 1,
    }

    assert result.substitutions is not None
    resolved = resolve_target_data(target_data, result.substitutions)
    assert resolved["a"][0] == "asdf-asdf"
    assert resolved["a"][1] == ["asdf-asdf", "asdf-asdf"]
    assert resolved["a"][2]["a"] == "asdf-asdf"
    assert resolved["d"] == "asdf-asdf"
