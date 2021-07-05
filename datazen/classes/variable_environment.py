"""
datazen - A child class for adding variable-data loading capabilities to the
          environment dataset.
"""

# built-in
from typing import List

# internal
from datazen import ROOT_NAMESPACE
from datazen.enums import DataType
from datazen.classes.base_environment import BaseEnvironment, LOADTYPE
from datazen.variables import load as load_variables


class VariableEnvironment(BaseEnvironment):
    """
    The variable-data loading environment mixin. Only requires the base
    environment capability to function.
    """

    def load_variables(
        self, var_loads: LOADTYPE = (None, None), name: str = ROOT_NAMESPACE
    ) -> dict:
        """Load variable data, resolve any un-loaded variable directories."""

        # determine directories that need to be loaded
        data_type = DataType.VARIABLE

        with self.lock:
            to_load = self.get_to_load(data_type, name)

            # load new data
            variable_data = self.get_data(data_type, name)
            if to_load:
                variable_data.update(
                    load_variables(to_load, var_loads[0], var_loads[1])
                )
                self.update_load_state(data_type, to_load, name)

        return variable_data

    def add_variable_dirs(
        self,
        dir_paths: List[str],
        rel_path: str = ".",
        name: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
    ) -> int:
        """
        Add variable-data directories, return the number of directories added.
        """

        return self.add_dirs(
            DataType.VARIABLE, dir_paths, rel_path, name, allow_dup
        )
