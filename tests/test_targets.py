
"""
datazen - Test functions in the 'targets' module.
"""

# module under test
from datazen.paths import unflatten_dict
from datazen.targets import parse_target, match_target, resolve_target_data


def test_parse_target_hiera():
    """ Test a pattern-matching case with delimeters in the key name. """

    regex, keys = parse_target("test-{a.b.c}-target")
    assert "a.b.c" in keys
    target = "test-hello-target"
    result = match_target(target, regex, keys)
    assert result[0]
    assert "a.b.c" in result[1]
    assert result[1]["a.b.c"] == "hello"
    assert unflatten_dict(result[1]) == {"a": {"b": {"c": "hello"}}}

    target = "test-asdf.asdf-target"
    result = match_target(target, regex, keys)
    assert result[0]
    assert "a.b.c" in result[1]
    assert result[1]["a.b.c"] == "asdf.asdf"


def test_parse_target_basic():
    """ Test some simple pattern-matching cases. """

    regex, keys = parse_target("test-{named}-target")
    assert "named" in keys
    target = "test-hello-target"
    result = match_target(target, regex, keys)
    assert result[0]
    assert "named" in result[1]
    assert result[1]["named"] == "hello"

    # test a match that includes a dash and an underscore
    target = "test-hello-hello_hello-target"
    result = match_target(target, regex, keys)
    assert result[0]
    assert "named" in result[1]
    assert result[1]["named"] == "hello-hello_hello"

    regex, keys = parse_target("{test1}-{test2}")
    assert "test1" in keys
    assert "test2" in keys
    target = "asdf-asdf"
    result = match_target(target, regex, keys)
    assert result[0]
    assert "test1" in result[1]
    assert "test2" in result[1]
    assert result[1]["test1"] == "asdf"
    assert result[1]["test2"] == "asdf"

    target_data = {"a": ["{test1}-{test2}",
                         ["{test1}-{test2}", "{test1}-{test2}"],
                         {"a": "{test1}-{test2}", "b": "asdf"}, 1],
                   "b": {},
                   "c": {"a": [], "b": "{test1}", "c": "{test2}"},
                   "d": "{test1}-{test2}",
                   "e": 1}
    result = resolve_target_data(target_data, result[1])
    assert result["a"][0] == "asdf-asdf"
    assert result["a"][1] == ["asdf-asdf", "asdf-asdf"]
    assert result["a"][2]["a"] == "asdf-asdf"
    assert result["d"] == "asdf-asdf"

    target = "literal_target"
    regex, keys = parse_target(target)
    assert not keys
    result = match_target(target, regex, keys)
    assert result[0]
    result = match_target("fail", regex, keys)
    assert not result[0]
