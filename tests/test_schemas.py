"""
datazen - Tests for the 'schemas' API.
"""

# module under test
from datazen.schemas import validate

# internal
from . import ENV


def test_load_schemas():
    """Test that the schemas can be loaded."""

    assert ENV.get_schemas(True, True)


def test_validate_configs():
    """Test that schema data can successfully validate configuration data."""

    schema_data = ENV.get_schemas(True, True)
    assert schema_data
    config_data = ENV.get_configs(True)
    assert config_data

    assert validate(schema_data, config_data)
