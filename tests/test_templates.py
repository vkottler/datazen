
"""
datazen - Tests for the 'templates' API.
"""

# internal
from . import ENV


def test_load_templates():
    """ Test that the templates can be loaded. """

    template_keys = ["a", "b", "c"]
    templates = ENV.get_templates(True)

    for key in template_keys:
        assert templates[key]
        templates[key].render(ENV.get_configs(True))
