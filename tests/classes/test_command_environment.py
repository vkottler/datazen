
"""
datazen - Tests for the 'CommandEnvironment' class mixin.
"""

# module under test
from datazen.classes.environment import from_manifest

# internal
from ..resources import get_resource, scoped_environment


def test_command_duplicate_matches():
    """ Test a scenario where two target patterns match a String. """

    with scoped_environment("manifest.yaml", True) as env:
        assert env.command("bad-pattern-test-asdf") == (False, False)


def test_command_basic():
    """ Test basic commanding functionality. """

    with scoped_environment("manifest.yaml", True) as env:
        # run a command
        assert env.command("a") == (True, True)
        assert env.command("b") == (True, True)
        assert env.command("a") == (True, False)
        assert env.command("false") == (False, True)

        # test templated commands
        assert env.command("echo-asdf") == (True, True)
        assert env.command("echo-asdf") == (True, False)
        assert env.command("echo-asdfasdf") == (True, True)
        assert env.command("echo-asdfasdf") == (True, False)
        assert env.command("ECHO-asdf") == (False, False)

        env.write_cache()
        new_env = from_manifest(get_resource("manifest.yaml", True))
        assert new_env.command("a") == (True, False)
