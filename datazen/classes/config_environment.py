
"""
datazen - A child class for adding configuration-data loading capabilities to
          the environment dataset.
"""

# built-in
import logging

# internal
from datazen.classes.base_environment import DataType
from datazen.classes.variable_environment import VariableEnvironment
from datazen.configs import load as load_configs

LOG = logging.getLogger(__name__)


class ConfigEnvironment(VariableEnvironment):
    """
    The configuration-data loading environment mixin, requires variable
    loading to function.
    """

    def load_configs(self) -> dict:
        """
        Load configuration data, resolve any un-loaded configuration
        directories.
        """

        # determine directories that need to be loaded
        data_type = DataType.CONFIG
        to_load = self.get_to_load(data_type)

        # load new data
        config_data = self.data[data_type]
        if to_load:
            config_data.update(load_configs(to_load, self.load_variables()))
            self.update_load_state(data_type, to_load)

        return config_data
