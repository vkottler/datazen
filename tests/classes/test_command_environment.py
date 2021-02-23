
"""
datazen - Tests for the 'CommandEnvironment' class mixin.
"""

# module under test
from datazen.classes.environment import from_manifest

# internal
from ..resources import get_resource


def test_command_basic():
    """ Test basic commanding functionality. """

    manifest = get_resource("manifest.yaml", True)
    env = from_manifest(manifest)
    env.clean_cache()

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
    env = from_manifest(manifest)
    assert env.command("a") == (True, False)

    env.clean_cache()
