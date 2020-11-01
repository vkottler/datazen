
"""
datazen - Top-level APIs for loading and interacting with templates.
"""

# built-in
from typing import List

# third-party
import jinja2


def get_template(template_dirs: List[str],
                 template_name: str) -> jinja2.Template:
    """
    Load a jinja2 template from a list of directories where templates may
    exist, and a name of a template to load.
    """

    # load specific template
    return jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dirs, followlinks=True),
            trim_blocks=True,
            lstrip_blocks=True
    ).get_template(template_name)
