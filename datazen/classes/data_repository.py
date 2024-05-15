"""
datazen - An interface for managing on-disk data by loading it and making
          discrete changes.
"""

# built-in
from contextlib import contextmanager
import logging
import os
import threading
from typing import Iterator

# third-party
from git import Repo
from vcorelib.dict import GenericStrDict, merge

# internal
from datazen.compile import write_dir
from datazen.load import load_dir_only
from datazen.paths import EXCLUDES


class DataRepository:
    """
    A class for interacting with file-backed databases that are built with
    serialization formats supported by this package.
    """

    def __init__(
        self,
        root_dir: str,
        out_type: str = "yaml",
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        """Construct a new data repository."""

        self.root: str = os.path.realpath(root_dir)
        self.out_type = out_type
        self.repo = Repo(self.root)
        # we should store some useful state - maybe what branch / head we're on
        # we may even want to split out the git stuff into its own class
        self.data: GenericStrDict = {}
        self.lock = threading.RLock()
        self.logger = logger

    def _update_data(
        self,
        data: GenericStrDict,
        root_rel: str = ".",
        expect_overwrite: bool = False,
    ) -> None:
        """Update internal data with loaded contents."""

        # update data with contents provided
        with self.loaded(root_rel) as curr_data:
            self.data = merge(
                curr_data, data, expect_overwrite=expect_overwrite
            )

    @contextmanager
    def meld(
        self,
        data: GenericStrDict,
        root_rel: str = ".",
        expect_overwrite: bool = False,
    ) -> Iterator[Repo]:
        """
        Update the data at some root-relative path, write it to disk and then
        provided the repository object still within a locked context.
        """

        with self.lock:
            self._update_data(
                data, root_rel=root_rel, expect_overwrite=expect_overwrite
            )

            # yield the repository after we've written disk but before
            # releasing the lock
            yield self.repo

    @contextmanager
    def loaded(
        self, root_rel: str = ".", write_back: bool = True
    ) -> Iterator[GenericStrDict]:
        """
        Load a data directory, yield it to the caller and write it back when
        complete inside a locked context for this repository.
        """

        to_load = os.path.realpath(os.path.join(self.root, root_rel))
        assert os.path.isdir(to_load)
        with self.lock:
            self.data = load_dir_only(to_load)[0]
            self.logger.info("loading '%s'", to_load)
            yield self.data
            if write_back:
                # remove items that contain data but not others
                for item in os.listdir(to_load):
                    if item not in EXCLUDES:
                        os.remove(os.path.join(to_load, item))
                write_dir(to_load, self.data, self.out_type)
                self.logger.info("writing '%s'", to_load)
