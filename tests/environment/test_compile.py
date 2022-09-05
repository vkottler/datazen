"""
datazen - Tests for the 'CompileEnvironment' class mixin.
"""

# module under test
from datazen.environment.base import TaskResult

# internal
from ..resources import scoped_environment, scoped_scenario


def test_compile_overrides():
    """Test compiles that use overrides."""

    with scoped_environment() as env:
        assert env.group("compile-test") == TaskResult(True, True)
        assert env.compile("unmerged-comp2-e") == TaskResult(False, False)


def test_ini_basic():
    """Test some compile targets that interact with INI data."""

    with scoped_scenario("test_ini") as env:
        for key in "abc":
            assert env.compile(f"single-{key}").success
        assert not env.compile("bad").success
