
"""
datazen - A testing environment class for aggregating commonly used test data.
"""

# built-in
from typing import Dict

# third-party
import jinja2

# modules under test
from datazen.classes.environment import Environment

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
        dirs = get_test_configs(True)
        assert self.valid.add_config_dirs(dirs) == len(dirs)

        # add schema directories
        dirs = get_test_schemas(True)
        assert self.valid.add_schema_dirs(dirs) == len(dirs)

        # add template directories
        dirs = get_test_templates(True)
        assert self.valid.add_template_dirs(dirs) == len(dirs)

        # add variable directories
        dirs = get_test_variables(True)
        assert self.valid.add_variable_dirs(dirs) == len(dirs)

        self.invalid = Environment()

    def get_configs(self, valid: bool = True) -> dict:
        """ Attempt to load one of the sets of configuration data. """

        env = self.valid if valid else self.invalid
        return env.load_configs()

    def get_schemas(self, valid: bool = True,
                    require_all: bool = True) -> dict:
        """ Attempt to load one of the sets of schemas. """

        env = self.valid if valid else self.invalid
        return env.load_schemas(require_all)

    def get_templates(self, valid: bool = True) -> Dict[str, jinja2.Template]:
        """ Attempt to load one of the sets of templates. """

        env = self.valid if valid else self.invalid
        return env.load_templates()

    def get_variables(self, valid: bool = True) -> dict:
        """ Attempt to load one of the sets of variables. """

        env = self.valid if valid else self.invalid
        return env.load_variables()
