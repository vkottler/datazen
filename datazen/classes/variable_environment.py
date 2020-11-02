
"""
datazen - TODO.
"""

# built-in
import logging

# internal
from datazen.classes.base_environment import BaseEnvironment, DataType
from datazen.variables import load as load_variables

LOG = logging.getLogger(__name__)


class VariableEnvironment(BaseEnvironment):
    """ TODO """

    def load_variables(self) -> dict:
        """ TODO """

        # determine directories that need to be loaded
        data_type = DataType.VARIABLE
        to_load = self.get_to_load(data_type)

        # load new data
        variable_data = self.data[data_type]
        if to_load:
            variable_data.update(load_variables(to_load))
            self.update_load_state(data_type, to_load)

        return variable_data
