"""
datazen - Tests for the data-repository class.
"""

# internal
from tests.resources import get_temp_repo

# module under test
from datazen.classes.data_repository import DataRepository


def test_data_repository_basic():
    """Verify that a simple data-repository use case works."""

    with get_temp_repo() as repo_root:
        repo = DataRepository(repo_root)
        with repo.meld(
            {"a": {"a": 1}, "b": {"b": 2}, "c": {"c": 3}}
        ) as git_repo:
            # make sure data is stored on disk
            assert all(
                x in git_repo.untracked_files
                for x in ["a.yaml", "b.yaml", "c.yaml"]
            )
        # expect a file to be deleted if we drop a key
        with repo.loaded() as data:
            del data["c"]
        assert "c.yaml" not in repo.repo.untracked_files
