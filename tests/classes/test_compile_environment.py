
"""
datazen - Tests for the 'CompileEnvironment' class mixin.
"""

# internal
from ..resources import scoped_environment


def test_compile_overrides():
    """ Test compiles that use overrides. """

    with scoped_environment("manifest.yaml", True) as env:
        assert env.group("compile-test") == (True, True)
