
"""
datazen - A child class for adding configuration-data loading capabilities to
          the environment dataset.
"""

# built-in
import logging
from typing import List

# internal
from datazen.classes.base_environment import DataType
from datazen.classes.variable_environment import VariableEnvironment
from datazen.classes.schema_environment import SchemaEnvironment
from datazen.configs import load as load_configs

LOG = logging.getLogger(__name__)


class ConfigEnvironment(VariableEnvironment, SchemaEnvironment):
    """
    The configuration-data loading environment mixin, requires variable
    loading to function.
    """

    def load_configs(self) -> dict:
        """
        Load configuration data, resolve any un-loaded configuration
        directories.
        """

        self.configs_valid = False

        # determine directories that need to be loaded
        data_type = DataType.CONFIG
        to_load = self.get_to_load(data_type)

        # load new data
        config_data = self.data[data_type]
        if to_load:
            config_data.update(load_configs(to_load, self.load_variables()))
            self.update_load_state(data_type, to_load)

        # enforce schemas
        if not self.enforce_schemas(config_data):
            LOG.error("schema validation failed, returning an empty dict")
            return {}

        self.configs_valid = True
        return config_data

    def add_config_dirs(self, dir_paths: List[str]) -> int:
        """
        Add configuration-data directories, return the number of directories
        added.
        """

        return self.add_dirs(DataType.CONFIG, dir_paths)
