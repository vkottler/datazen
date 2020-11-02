
"""
datazen - Top-level APIs for loading and interacting with templates.
"""

# built-in
from typing import Dict, List

# third-party
import jinja2

# internal
from datazen.paths import get_file_name, get_file_ext


def load(template_dirs: List[str]) -> Dict[str, jinja2.Template]:
    """
    Load jinja2 templates from a list of directories where templates can be
    found.
    """

    result = {}

    # setup jinja environment
    loader = jinja2.FileSystemLoader(template_dirs, followlinks=True)
    env = jinja2.Environment(loader=loader, trim_blocks=True,
                             lstrip_blocks=True)

    # load templates into a dictionary
    for template in env.list_templates():
        key = get_file_name(template)
        assert get_file_ext(template) == "j2"
        result[key] = env.get_template(template)
    return result
