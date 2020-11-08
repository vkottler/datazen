
"""
datazen - A child class for adding configuration-data loading capabilities to
          the environment dataset.
"""

# built-in
import logging
from typing import Dict, List, Tuple, Optional

# internal
from datazen.classes.base_environment import DataType
from datazen.classes.variable_environment import VariableEnvironment
from datazen.classes.schema_environment import SchemaEnvironment
from datazen.configs import load as load_configs

LOG = logging.getLogger(__name__)
LOADTYPE = Tuple[Optional[List[str]], Optional[Dict[str, str]]]


class ConfigEnvironment(VariableEnvironment, SchemaEnvironment):
    """
    The configuration-data loading environment mixin, requires variable
    loading to function.
    """

    def load_configs(self, config_loads: LOADTYPE = (None, None),
                     variable_loads: LOADTYPE = (None, None),
                     schema_loads: LOADTYPE = (None, None)) -> dict:
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
            vdata = self.load_variables(variable_loads[0], variable_loads[1])
            config_data.update(load_configs(to_load, vdata, config_loads[0],
                                            config_loads[1]))
            self.update_load_state(data_type, to_load)

        # enforce schemas
        if not self.enforce_schemas(config_data, True, schema_loads[0],
                                    schema_loads[1]):
            LOG.error("schema validation failed, returning an empty dict")
            return {}

        self.configs_valid = True
        return config_data

    def add_config_dirs(self, dir_paths: List[str],
                        rel_path: str = ".") -> int:
        """
        Add configuration-data directories, return the number of directories
        added.
        """

        return self.add_dirs(DataType.CONFIG, dir_paths, rel_path)
