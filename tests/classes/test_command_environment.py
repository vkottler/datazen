
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

    env.clean_cache()
