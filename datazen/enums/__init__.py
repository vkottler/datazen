"""
datazen - A module for various package enumerations.
"""

# built-in
from enum import Enum


class DataType(Enum):
    """The discrete types of information that can be loaded."""

    CONFIG = "config"
    SCHEMA = "schema"
    SCHEMA_TYPES = "schema_type"
    TEMPLATE = "template"
    VARIABLE = "variable"
