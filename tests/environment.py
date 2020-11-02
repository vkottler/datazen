
"""
datazen - A testing environment class for aggregating commonly used test data.
"""

# built-in
from typing import Dict

# third-party
import jinja2

# modules under test
from datazen.schemas import load as load_schemas
from datazen.templates import load as load_templates
from datazen.classes.environment import Environment
from datazen.classes.base_environment import DataType

# internal
from .resources import (
    get_test_configs,
    get_test_schemas,
    get_test_templates,
    get_test_variables,
)


class EnvironmentMock:
    """ A class for simple test-data access. """

    def __init__(self):
        """ Initialize data storage. """

        self.valid = Environment()

        # add config directories
        for config_dir in get_test_configs(True):
            assert self.valid.add_dir(DataType.CONFIG, config_dir)

        # add schema directories
        for schema_dir in get_test_schemas(True):
            assert self.valid.add_dir(DataType.SCHEMA, schema_dir)

        # add template directories
        for template_dir in get_test_templates(True):
            assert self.valid.add_dir(DataType.TEMPLATE, template_dir)

        # add variable directories
        for variable_dir in get_test_variables(True):
            assert self.valid.add_dir(DataType.VARIABLE, variable_dir)

        self.invalid = Environment()

        self.valid_raw = {}
        self.invalid_raw = {}

    def get_configs(self, valid: bool = True) -> dict:
        """ Attempt to load one of the sets of configuration data. """

        env = self.valid if valid else self.invalid
        return env.load_configs()

    def get_schemas(self, valid: bool = True,
                    require_all: bool = True) -> dict:
        """ Attempt to load one of the sets of schemas. """

        root = self.valid_raw if valid else self.invalid_raw
        if "schemas" not in root:
            root["schemas"] = load_schemas(get_test_schemas(valid),
                                           require_all)
        return root["schemas"]

    def get_templates(self, valid: bool = True) -> Dict[str, jinja2.Template]:
        """ Attempt to load one of the sets of templates. """

        root = self.valid_raw if valid else self.invalid_raw
        if "templates" not in root:
            root["templates"] = load_templates(get_test_templates())
        return root["templates"]

    def get_variables(self, valid: bool = True) -> dict:
        """ Attempt to load one of the sets of variables. """

        env = self.valid if valid else self.invalid
        return env.load_variables()
