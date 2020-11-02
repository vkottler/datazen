
"""
datazen - A child class for adding schema-data loading capabilities to the
          environment dataset.
"""

# internal
from datazen.classes.base_environment import BaseEnvironment, DataType
from datazen.schemas import load as load_schemas
from datazen.schemas import validate


class SchemaEnvironment(BaseEnvironment):
    """
    The schema-data loading environment mixin, only requires the base
    environment capability to function.
    """

    def load_schemas(self, require_all: bool = True) -> dict:
        """ Load schema data, resolve any un-loaded schema directories. """

        # determine directories that need to be loaded
        data_type = DataType.SCHEMA
        to_load = self.get_to_load(data_type)

        # load new data
        schema_data = self.data[data_type]
        if to_load:
            schema_data.update(load_schemas(to_load, require_all))

        return schema_data

    def enforce_schemas(self, data: dict, require_all: bool = True) -> bool:
        """
        Perform schema-validation on provided data and return the boolean
        result.
        """

        return validate(self.load_schemas(require_all), data)
