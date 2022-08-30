"""
datazen - Tests for the 'templates' API.
"""

# internal
from . import ENV


def test_load_templates():
    """Test that the templates can be loaded."""

    template_keys = ["a", "b", "c"]
    templates = ENV.get_templates(True)

    configs = ENV.get_configs(True)
    configs["global"] = configs

    for key in template_keys:
        assert templates[key]
        templates[key].render(configs)

    del configs["global"]
