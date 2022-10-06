"""
datazen - A child class for adding schema-data loading capabilities to the
          environment dataset.
"""

# built-in
from typing import List

# third-party
from vcorelib.dict import GenericStrDict

# internal
from datazen import ROOT_NAMESPACE
from datazen.enums import DataType
from datazen.environment.base import BaseEnvironment
from datazen.load import DEFAULT_LOADS, LoadedFiles
from datazen.schemas import inject_custom_schemas
from datazen.schemas import load as load_schemas
from datazen.schemas import load_types, validate


class SchemaEnvironment(BaseEnvironment):
    """
    The schema-data loading environment mixin, only requires the base
    environment capability to function.
    """

    def load_schema_types(
        self,
        sch_loads: LoadedFiles = DEFAULT_LOADS,
        name: str = ROOT_NAMESPACE,
    ) -> GenericStrDict:
        """Load custom schema types and resolve any un-loaded directories."""

        # determine directories that need to be loaded
        data_type = DataType.SCHEMA_TYPES

        with self.lock:
            to_load = self.get_to_load(data_type, name)

            # load schema data for this namespace
            schema_type_data = self.get_data(data_type, name)
            if to_load:
                schema_type_data.update(load_types(to_load, sch_loads))

        return schema_type_data

    def load_schemas(
        self,
        require_all: bool = True,
        sch_loads: LoadedFiles = DEFAULT_LOADS,
        sch_types_loads: LoadedFiles = DEFAULT_LOADS,
        name: str = ROOT_NAMESPACE,
        modify_registry: bool = True,
    ) -> GenericStrDict:
        """Load schema data, resolve any un-loaded schema directories."""

        # determine directories that need to be loaded
        data_type = DataType.SCHEMA

        sch_types = self.load_schema_types(sch_types_loads, name)

        with self.lock:
            to_load = self.get_to_load(data_type, name)

            # load new data
            schema_data = self.get_data(data_type, name)
            if to_load:
                with inject_custom_schemas(sch_types, modify_registry):
                    schema_data.update(
                        load_schemas(to_load, require_all, sch_loads)
                    )

        return schema_data

    def enforce_schemas(
        self,
        data: GenericStrDict,
        require_all: bool = True,
        sch_loads: LoadedFiles = DEFAULT_LOADS,
        sch_types_loads: LoadedFiles = DEFAULT_LOADS,
        name: str = ROOT_NAMESPACE,
    ) -> bool:
        """
        Perform schema-validation on provided data and return the boolean
        result. Adds (and removes) namespaced types if applicable.
        """

        with self.lock:
            sch_types = self.load_schema_types(sch_types_loads, name)
            with inject_custom_schemas(sch_types):
                result = validate(
                    self.load_schemas(
                        require_all, sch_loads, sch_types_loads, name, False
                    ),
                    data,
                    self.logger,
                )

        return result

    def add_schema_type_dirs(
        self,
        dir_paths: List[str],
        rel_path: str = ".",
        name: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
    ) -> int:
        """
        Add directories containing schema-type data (to be registered at
        runtime).
        """

        return self.add_dirs(
            DataType.SCHEMA_TYPES, dir_paths, rel_path, name, allow_dup
        )

    def add_schema_dirs(
        self,
        dir_paths: List[str],
        rel_path: str = ".",
        name: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
    ) -> int:
        """
        Add schema-data directories, return the number of directories added.
        """

        return self.add_dirs(
            DataType.SCHEMA, dir_paths, rel_path, name, allow_dup
        )
