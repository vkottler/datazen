"""
datazen - A dict wrapper that enables simpler schema validation.
"""

# built-in
from collections import UserDict
import logging

# third-party
from vcorelib.dict import GenericStrDict
from vcorelib.schemas.base import Schema, SchemaValidationError

LOG = logging.getLogger(__name__)


class ValidDict(UserDict):  # type: ignore
    """
    An object that behaves like a dictionary but can have a provided schema
    enforced.
    """

    def __init__(
        self,
        name: str,
        data: GenericStrDict,
        schema: Schema,
        logger: logging.Logger = LOG,
    ) -> None:
        """Initialize a named, ValidDict."""

        super().__init__(data)

        self.name = name
        self.logger = logger
        self.valid = False
        try:
            self.data = schema(self.data)
            self.valid = True
        except SchemaValidationError as exc:
            self.logger.error(
                "validation error(s) for '%s': %s", self.name, exc
            )
            self.logger.error("data: %s", self.data)
