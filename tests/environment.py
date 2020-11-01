
"""
datazen - TODO.
"""

# built-in
from typing import Dict

# third-party
import jinja2

# modules under test
from datazen.configs import load as load_configs
from datazen.variables import load as load_variables
from datazen.schemas import load as load_schemas
from datazen.templates import load as load_templates

# internal
from .resources import (
    get_test_configs,
    get_test_schemas,
    get_test_templates,
    get_test_variables,
)


class TestEnvironment:
    """ TODO """

    def __init__(self):
        """ TODO """

        self.valid = {}
        self.invalid = {}

    def get_configs(self, valid: bool = True) -> dict:
        """ TODO """

        root = self.valid if valid else self.invalid
        if "configs" not in root:
            root["configs"] = load_configs(get_test_configs(valid),
                                           self.get_variables(valid))
        return root["configs"]

    def get_schemas(self, valid: bool = True,
                    require_all: bool = True) -> dict:
        """ TODO """

        root = self.valid if valid else self.invalid
        if "schemas" not in root:
            root["schemas"] = load_schemas(get_test_schemas(valid),
                                           require_all)
        return root["schemas"]

    def get_templates(self, valid: bool = True) -> Dict[str, jinja2.Template]:
        """ TODO """

        root = self.valid if valid else self.invalid
        if "templates" not in root:
            root["templates"] = load_templates(get_test_templates())
        return root["templates"]

    def get_variables(self, valid: bool = True) -> dict:
        """ TODO """

        root = self.valid if valid else self.invalid
        if "variables" not in root:
            root["variables"] = load_variables(get_test_variables(valid))
        return root["variables"]
