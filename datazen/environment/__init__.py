"""
datazen - A data structure for runtime data.
"""

# built-in
from copy import copy, deepcopy
import logging
import os
import threading
from typing import Dict, List

# internal
from datazen.enums import DataType
from datazen.paths import resolve_dir


class EnvironmentNamespace:
    """The base class for management of the environment data structure."""

    def __init__(self, name: str):
        """Base constructor."""

        self.directories: Dict[DataType, List[dict]] = {}
        for dtype in DataType:
            self.directories[dtype] = []

        self.data: Dict[DataType, dict] = {}
        for dtype in DataType:
            self.data[dtype] = {}

        self.data_clone_strategy: Dict[DataType, dict] = {
            DataType.CONFIG: {"should": True, "method": deepcopy},
            DataType.SCHEMA: {"should": True, "method": deepcopy},
            DataType.SCHEMA_TYPES: {"should": False},
            DataType.VARIABLE: {"should": True, "method": deepcopy},
            DataType.TEMPLATE: {"should": True, "method": copy},
        }

        self.valid = True
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"namespace.{name}")

    def get_to_load(self, dir_type: DataType) -> List[str]:
        """
        Build a list of the yet-to-be-loaded directories for a given data
        type.
        """

        with self.lock:
            dir_data = self.directories[dir_type]

            to_load = []
            for dir_inst in dir_data:
                if not dir_inst["loaded"]:
                    to_load.append(dir_inst["path"])

        return to_load

    def unload(self, dir_type: DataType) -> None:
        """Mark all directories for a given type as un-loaded."""

        with self.lock:
            for dir_inst in self.directories[dir_type]:
                dir_inst["loaded"] = False
            self.data[dir_type] = {}

    def unload_all(self) -> None:
        """Mark all directories as unloaded."""

        for key in self.data:
            self.unload(key)

    def update_load_state(self, dir_type: DataType, to_load: List[str]) -> int:
        """
        Update the load states of directories in 'to_load' for a given
        data type.
        """

        with self.lock:
            dir_data = self.directories[dir_type]
            loaded = 0

            for dir_inst in dir_data:
                if dir_inst["path"] in to_load:
                    self.logger.debug(
                        "loaded '%s' as '%s'", dir_inst["path"], dir_type.value
                    )
                    dir_inst["loaded"] = True
                    loaded = loaded + 1

        self.logger.debug(
            "loaded %d new directories for '%s'", loaded, dir_type.value
        )

        return loaded

    def add_dir(
        self,
        dir_type: DataType,
        dir_path: str,
        rel_path: str = ".",
        allow_dup: bool = False,
    ) -> bool:
        """Add a directory to be loaded for a given data type."""

        with self.lock:
            dir_list = self.directories[dir_type]
            dir_path = resolve_dir(dir_path, rel_path)

            for dir_data in dir_list:
                if dir_path == dir_data["path"]:

                    def noop(*_, **__):
                        pass

                    log_fn = noop if allow_dup else noop
                    log_fn(
                        "not adding duplicate directory '%s' to '%s'",
                        dir_path,
                        dir_type.value,
                    )
                    return allow_dup

            if not os.path.isdir(dir_path):
                self.logger.error(
                    "'%s' isn't a directory, not adding to '%s'",
                    dir_path,
                    dir_type.value,
                )
                return False

            dir_list.append({"path": dir_path, "loaded": False})

        self.logger.debug("added '%s' to '%s'", dir_path, dir_type.value)
        return True

    def add_dirs(
        self,
        dir_type: DataType,
        dir_paths: List[str],
        rel_path: str = ".",
        allow_dup: bool = False,
    ) -> int:
        """
        Add multiple directories for a given data type, return the number of
        directories added.
        """

        dirs_added = 0

        for dir_path in dir_paths:
            if self.add_dir(dir_type, dir_path, rel_path, allow_dup):
                dirs_added = dirs_added + 1

        if dirs_added != len(dir_paths):
            self.logger.error(
                "only loaded %d / %d directories, marking invalid",
                dirs_added,
                len(dir_paths),
            )
            self.valid = False

        return dirs_added


def clone(
    env: EnvironmentNamespace, update: EnvironmentNamespace
) -> EnvironmentNamespace:
    """Create a clone (deep copy) of an existing Environment."""

    with env.lock:
        # all we need to do is copy all of the attributes
        update.directories = deepcopy(env.directories)

        # clone data based on the source's strategy
        for dtype, strat in env.data_clone_strategy.items():
            if strat["should"]:
                update.data[dtype] = strat["method"](env.data[dtype])

        update.valid = env.valid

    return update
