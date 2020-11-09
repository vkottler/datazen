
"""
datazen - A testing environment class for aggregating commonly used test data.
"""

# built-in
import os
from typing import Dict

# third-party
import jinja2

# modules under test
from datazen.classes.environment import from_manifest

# internal
from .resources import get_resource


class EnvironmentMock:
    """ A class for simple test-data access. """

    def __init__(self):
        """ Initialize data storage. """

        manifest_path = get_resource(os.path.join("manifests", "test.yaml"),
                                     True)
        self.valid = from_manifest(manifest_path)
        assert self.valid.get_valid()

        manifest_path = get_resource(os.path.join("manifests", "valid.yaml"),
                                     False)
        self.invalid = from_manifest(manifest_path)
        assert self.invalid.get_valid()

    def get_configs(self, valid: bool = True) -> dict:
        """ Attempt to load one of the sets of configuration data. """

        env = self.valid if valid else self.invalid
        return env.cached_load_configs()

    def get_schemas(self, valid: bool = True,
                    require_all: bool = True) -> dict:
        """ Attempt to load one of the sets of schemas. """

        env = self.valid if valid else self.invalid
        return env.cached_load_schemas(require_all)

    def get_templates(self, valid: bool = True) -> Dict[str, jinja2.Template]:
        """ Attempt to load one of the sets of templates. """

        env = self.valid if valid else self.invalid
        return env.load_templates()

    def get_variables(self, valid: bool = True) -> dict:
        """ Attempt to load one of the sets of variables. """

        env = self.valid if valid else self.invalid
        return env.cached_load_variables()
