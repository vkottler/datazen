
"""
datazen - TODO.
"""

# built-in
import logging

# internal
from datazen.classes.base_environment import DataType
from datazen.classes.variable_environment import VariableEnvironment
from datazen.configs import load as load_configs

LOG = logging.getLogger(__name__)


class ConfigEnvironment(VariableEnvironment):
    """ TODO """

    def load_configs(self) -> dict:
        """ TODO """

        # determine directories that need to be loaded
        data_type = DataType.CONFIG
        to_load = self.get_to_load(data_type)

        # load new data
        config_data = self.data[data_type]
        if to_load:
            config_data.update(load_configs(to_load, self.load_variables()))
            self.update_load_state(data_type, to_load)

        return config_data
