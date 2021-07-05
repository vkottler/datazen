"""
datazen - A dict wrapper that enables simpler schema validation.
"""

# built-in
import logging
from collections import UserDict

# third-party
from cerberus import Validator

LOG = logging.getLogger(__name__)


class ValidDict(UserDict):
    """
    An object that behaves like a dictionary but can have a provided schema
    enforced.
    """

    def __init__(self, name: str, data: dict, schema: Validator):
        """Initialize a named, ValidDict."""

        # initialize the dict
        if not isinstance(data, dict):
            data = {}
        super().__init__(data)

        self.name = name
        self.validator = schema
        self.valid = self.validator.validate(self.data)
        if not self.valid:
            LOG.error(
                "validation error(s) for '%s': %s",
                self.name,
                self.validator.errors,
            )
            LOG.error("data: %s", data)
            LOG.error("schema: %s", schema.schema)
