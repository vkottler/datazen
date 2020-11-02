
"""
datazen - A base class to be extended for runtime data loading and storing.
"""

# built-in
from enum import Enum
import logging
import os
from typing import List

LOG = logging.getLogger(__name__)


class DataType(Enum):
    """ The discrete types of information that can be loaded. """

    CONFIG = "config"
    SCHEMA = "schema"
    TEMPLATE = "template"
    VARIABLE = "variable"


class BaseEnvironment:
    """ The base class for environment loading-and-storing management. """

    def __init__(self):
        """ Base constructor. """

        self.directories = {
            DataType.CONFIG: [],
            DataType.SCHEMA: [],
            DataType.TEMPLATE: [],
            DataType.VARIABLE: [],
        }

        self.data = {
            DataType.CONFIG: {},
            DataType.SCHEMA: {},
            DataType.TEMPLATE: {},
            DataType.VARIABLE: {},
        }

        self.configs_valid = False

    def get_to_load(self, dir_type: DataType) -> List[str]:
        """
        Build a list of the yet-to-be-loaded directories for a given data
        type.
        """

        dir_data = self.directories[dir_type]

        to_load = []
        for dir_inst in dir_data:
            if not dir_inst["loaded"]:
                to_load.append(dir_inst["path"])
        return to_load

    def update_load_state(self, dir_type: DataType, to_load: List[str]) -> int:
        """
        Update the load states of directories in 'to_load' for a given
        data type.
        """

        dir_data = self.directories[dir_type]
        loaded = 0

        for dir_inst in dir_data:
            if dir_inst["path"] in to_load:
                LOG.info("loaded '%s' as '%s'", dir_inst["path"],
                         dir_type.value)
                dir_inst["loaded"] = True
                loaded = loaded + 1

        LOG.debug("loaded %d new directories for '%s'", loaded, dir_type.value)

        return loaded

    def add_dir(self, dir_type: DataType, dir_path: str) -> bool:
        """ Add a directory to be loaded for a given data type. """

        dir_list = self.directories[dir_type]

        for dir_data in dir_list:
            if dir_path == dir_data["path"]:
                LOG.error("not adding duplicate directory '%s' to '%s'",
                          dir_path, dir_type.value)
                return False

        if not os.path.isdir(dir_path):
            LOG.error("'%s' isn't a directory, not adding to '%s'", dir_path,
                      dir_type.value)
            return False

        dir_list.append({"path": dir_path, "loaded": False})
        LOG.info("added '%s' to '%s'", dir_path, dir_type.value)
        return True

    def add_dirs(self, dir_type: DataType, dir_paths: List[str]) -> int:
        """
        Add multiple directories for a given data type, return the number of
        directories added.
        """

        dirs_added = 0
        for dir_path in dir_paths:
            if self.add_dir(dir_type, dir_path):
                dirs_added = dirs_added + 1
        return dirs_added
