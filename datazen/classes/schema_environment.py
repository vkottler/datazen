
"""
datazen - A child class for adding schema-data loading capabilities to the
          environment dataset.
"""

# built-in
from typing import List

# internal
from datazen import ROOT_NAMESPACE
from datazen.enums import DataType
from datazen.classes.base_environment import BaseEnvironment, LOADTYPE
from datazen.schemas import load as load_schemas
from datazen.schemas import validate


class SchemaEnvironment(BaseEnvironment):
    """
    The schema-data loading environment mixin, only requires the base
    environment capability to function.
    """

    def load_schemas(self, require_all: bool = True,
                     sch_loads: LOADTYPE = (None, None),
                     name: str = ROOT_NAMESPACE) -> dict:
        """ Load schema data, resolve any un-loaded schema directories. """

        # determine directories that need to be loaded
        data_type = DataType.SCHEMA
        to_load = self.get_to_load(data_type, name)

        # load new data
        schema_data = self.get_data(data_type, name)
        if to_load:
            schema_data.update(load_schemas(to_load, require_all, sch_loads[0],
                                            sch_loads[1]))

        return schema_data

    def enforce_schemas(self, data: dict, require_all: bool = True,
                        sch_loads: LOADTYPE = (None, None),
                        name: str = ROOT_NAMESPACE) -> bool:
        """
        Perform schema-validation on provided data and return the boolean
        result.
        """

        return validate(self.load_schemas(require_all, sch_loads, name), data)

    def add_schema_dirs(self, dir_paths: List[str], rel_path: str = ".",
                        name: str = ROOT_NAMESPACE,
                        allow_dup: bool = False) -> int:
        """
        Add schema-data directories, return the number of directories added.
        """

        return self.add_dirs(DataType.SCHEMA, dir_paths, rel_path, name,
                             allow_dup)
