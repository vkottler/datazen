"""
datazen - Test the program's entry-point.
"""

# built-in
import os
from subprocess import check_output
from sys import executable

# module under test
from datazen import PKG_NAME
from datazen.entry import main as datazen_main

# internal
from .resources import get_resource


def test_entry_basic():
    """
    Build the default target to provide a useful test when isolating
    individual tests.
    """

    manifest = get_resource("manifest.yaml", True)
    args = [PKG_NAME, "-m", manifest]
    assert datazen_main(args) == 0
    assert datazen_main(args + ["-c"]) == 0


def test_package_entry():
    """Test the command-line entry through the 'python -m' invocation."""

    check_output([executable, "-m", PKG_NAME, "-h"])


def test_entry():
    """Test some basic command-line argument scenarios."""

    manifest = get_resource("manifest.yaml", True)
    manifest_dir = os.path.dirname(manifest)
    args = [PKG_NAME, "-m", manifest]

    assert datazen_main(args + ["--not-an-option", "asdf"]) != 0

    assert datazen_main(args) == 0
    assert datazen_main(args + ["-c"]) == 0
    assert datazen_main(args + ["a", "b", "c"]) == 0
    assert datazen_main(args + ["-c"]) == 0
    assert datazen_main(args + ["not_a_target"]) != 0
    assert datazen_main(args + ["--sync", "-d"]) == 0
    assert datazen_main([PKG_NAME, "-C", manifest_dir, "a", "b", "c"]) == 0
    assert datazen_main(args + ["--sync", "-d"]) == 0

    # change a file to test describe's miss detection
    data_file = get_resource(os.path.join("configs", "a.yaml"), True)
    with open(data_file, encoding="utf-8") as manifest_file:
        manifest_data = manifest_file.read()
    with open(data_file, "w", encoding="utf-8") as manifest_file:
        manifest_file.write("a: {{a}}")

    assert datazen_main(args + ["-d"]) == 0

    # remove a file to additionally test describe's miss detection
    os.remove(data_file)
    assert datazen_main(args + ["-d"]) == 0

    # restore the changed file
    with open(data_file, "w", encoding="utf-8") as manifest_file:
        manifest_file.write(manifest_data)

    assert datazen_main(args + ["-c"]) == 0

    # test inability to load a manifest
    assert datazen_main(args + ["-m", "not-a-manifest"]) != 0
