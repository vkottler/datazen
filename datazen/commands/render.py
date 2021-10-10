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
from datazen.environment.integrated import Environment
from datazen.parsing import load_stream

LOG = logging.getLogger(__name__)


def str_render(
    template: jinja2.Template,
    config_data_path: str,
    logger: logging.Logger = LOG,
) -> str:
    """Load configuration data and render a jinja2 template with it."""

    # load the configuration data from file
    with open(config_data_path, encoding="utf-8") as stream:
        config_data = load_stream(stream, config_data_path, logger).data

    return template.render(config_data)


def cmd_render(
    template_dirs: List[str],
    template_name: str,
    config_data_path: str,
    output_file_path: str,
    logger: logging.Logger = LOG,
) -> bool:
    """Render the desired template from loaded configuration data."""

    env = Environment()

    # add directories
    env.add_template_dirs(template_dirs)

    # load specific template
    template = env.load_templates()[template_name]

    # render the template to the output file, using the new data
    with open(output_file_path, "w", encoding="utf-8") as output:
        output.write(str_render(template, config_data_path, logger))

    logger.info(
        "'%s' rendered from '%s' (template: '%s')",
        output_file_path,
        config_data_path,
        template_name,
    )

    return True
