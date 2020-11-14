
"""
datazen - Test the program's entry-point.
"""

# built-in
import os

# module under test
from datazen import PKG_NAME
from datazen.entry import main as datazen_main

# internal
from .resources import get_resource


def test_entry():
    """ Test some basic command-line argument scenarios. """

    manifest = get_resource("manifest.yaml", True)
    manifest_dir = os.path.dirname(manifest)
    args = [PKG_NAME, "-m", manifest]

    assert datazen_main(args + ["--not-an-option", "asdf"]) != 0

    assert datazen_main(args) == 0
    assert datazen_main(args + ["a", "b", "c"]) == 0
    assert datazen_main(args + ["not_a_target"]) != 0
    assert datazen_main([PKG_NAME, "-C", manifest_dir, "a", "b", "c"]) == 0
    assert datazen_main(args + ["-c"]) == 0
