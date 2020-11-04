
"""
datazen - A child class for adding template-loading capabilities to the
          environment dataset.
"""

# built-in
from typing import Dict, List

# third-party
import jinja2

# internal
from datazen.classes.base_environment import BaseEnvironment, DataType
from datazen.templates import load as load_templates


class TemplateEnvironment(BaseEnvironment):
    """
    The template-loading environment mixin, only requires the base environment
    capability to function.
    """

    def load_templates(self) -> Dict[str, jinja2.Template]:
        """ Load templates, resolve any un-loaded template directories. """

        # determine directories that need to be loaded
        data_type = DataType.TEMPLATE
        to_load = self.get_to_load(data_type)

        # load new templates
        template_data = self.data[data_type]
        if to_load:
            template_data.update(load_templates(to_load))

        return template_data

    def add_template_dirs(self, dir_paths: List[str],
                          rel_path: str = ".") -> int:
        """
        Add template directories, return the number of directories added.
        """

        return self.add_dirs(DataType.TEMPLATE, dir_paths, rel_path)
