"""
datazen - A child class for adding configuration-data loading capabilities to
          the environment dataset.
"""

# built-in
import logging
from typing import List

# internal
from datazen import ROOT_NAMESPACE
from datazen.enums import DataType
from datazen.environment.variable import VariableEnvironment
from datazen.environment.schema import SchemaEnvironment
from datazen.configs import load as load_configs
from datazen.load import LoadedFiles, DEFAULT_LOADS


class ConfigEnvironment(VariableEnvironment, SchemaEnvironment):
    """
    The configuration-data loading environment mixin, requires variable
    loading to function.
    """

    def __init__(self):
        """Extend the environment with a notion of configs being valid."""

        super().__init__()
        self.configs_valid = False

    def load_configs(
        self,
        cfg_loads: LoadedFiles = DEFAULT_LOADS,
        var_loads: LoadedFiles = DEFAULT_LOADS,
        sch_loads: LoadedFiles = DEFAULT_LOADS,
        sch_types_loads: LoadedFiles = DEFAULT_LOADS,
        name: str = ROOT_NAMESPACE,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> dict:
        """
        Load configuration data, resolve any un-loaded configuration
        directories.
        """

        self.configs_valid = False

        # determine directories that need to be loaded
        data_type = DataType.CONFIG

        with self.lock:
            to_load = self.get_to_load(data_type, name)

            # load new data
            config_data = self.get_data(data_type, name)
            if to_load:
                vdata = self.load_variables(var_loads, name)
                config_data.update(load_configs(to_load, vdata, cfg_loads))
                self.update_load_state(data_type, to_load, name)

        # enforce schemas
        if not self.enforce_schemas(
            config_data, True, sch_loads, sch_types_loads, name
        ):
            logger.error("schema validation failed, returning an empty dict")
            return {}

        self.configs_valid = True
        return config_data

    def add_config_dirs(
        self,
        dir_paths: List[str],
        rel_path: str = ".",
        name: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
    ) -> int:
        """
        Add configuration-data directories, return the number of directories
        added.
        """

        return self.add_dirs(
            DataType.CONFIG, dir_paths, rel_path, name, allow_dup
        )
