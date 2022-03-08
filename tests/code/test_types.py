"""
fswdev - Test the 'datazen.code.types' module.
"""

# built-in
from pathlib import Path

# module under test
from datazen.code.types import FileExtension

# internal
from tests.resources import get_resource


def test_data_files_simple():
    """Test that we can find files that contain data."""

    root = Path(get_resource("configs"))
    for path in "abcdef":
        candidates = list(
            FileExtension.data_candidates(Path(root, path), True)
        )
        assert len(candidates) > 0

        candidates = list(
            FileExtension.data_candidates(Path(root, f"{path}.txt"), True)
        )
        assert len(candidates) > 0
