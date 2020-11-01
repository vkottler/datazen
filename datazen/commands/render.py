
"""
datazen - A command implementation for rendering configuration data (that has
          optionally been resolved from variables) based on provided and
          discovered templates.
"""

# built-in
import logging
from typing import List

# third-party
import jinja2

# internal
from datazen.parsing import update_dict_from_stream
from datazen.templates import get_template

LOG = logging.getLogger(__name__)


def str_render(template: jinja2.Template, config_data_path: str) -> str:
    """ Load configuration data and render a jinja2 template with it. """

    # load the configuration data from file
    with open(config_data_path) as stream:
        config_data = update_dict_from_stream(stream, config_data_path)

    return template.render(config_data)


def cmd_render(template_dirs: List[str], template_name: str,
               config_data_path: str, output_file_path: str) -> bool:
    """ Render the desired template from loaded configuration data. """

    # load specific template
    template = get_template(template_dirs, template_name)

    # render the template to the output file, using the new data
    with open(output_file_path, "w") as output:
        output.write(str_render(template, config_data_path))

    LOG.info("'%s' rendered from '%s' (template: '%s')", output_file_path,
             config_data_path, template_name)

    return True
