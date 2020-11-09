
"""
datazen - A child class for adding variable-data loading capabilities to the
          environment dataset.
"""

# built-in
from typing import List, Dict

# internal
from datazen.classes.base_environment import BaseEnvironment, DataType
from datazen.variables import load as load_variables


class VariableEnvironment(BaseEnvironment):
    """
    The variable-data loading environment mixin. Only requires the base
    environment capability to function.
    """

    def load_variables(self, loaded_list: List[str] = None,
                       hashes: Dict[str, str] = None) -> dict:
        """ Load variable data, resolve any un-loaded variable directories. """

        # determine directories that need to be loaded
        data_type = DataType.VARIABLE
        to_load = self.get_to_load(data_type)

        # load new data
        variable_data = self.get_data(data_type)
        if to_load:
            variable_data.update(load_variables(to_load, loaded_list, hashes))
            self.update_load_state(data_type, to_load)

        return variable_data

    def add_variable_dirs(self, dir_paths: List[str],
                          rel_path: str = ".") -> int:
        """
        Add variable-data directories, return the number of directories added.
        """

        return self.add_dirs(DataType.VARIABLE, dir_paths, rel_path)
