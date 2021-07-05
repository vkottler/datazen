"""
datazen - A child class for adding template-loading capabilities to the
          environment dataset.
"""

# built-in
from typing import Dict, List

# third-party
import jinja2

# internal
from datazen import ROOT_NAMESPACE
from datazen.enums import DataType
from datazen.classes.base_environment import BaseEnvironment, LOADTYPE
from datazen.templates import load as load_templates


class TemplateEnvironment(BaseEnvironment):
    """
    The template-loading environment mixin, only requires the base environment
    capability to function.
    """

    def load_templates(
        self,
        template_loads: LOADTYPE = (None, None),
        name: str = ROOT_NAMESPACE,
    ) -> Dict[str, jinja2.Template]:
        """Load templates, resolve any un-loaded template directories."""

        # determine directories that need to be loaded
        data_type = DataType.TEMPLATE

        with self.lock:
            to_load = self.get_to_load(data_type, name)

            # load new templates
            template_data = self.get_data(data_type, name)
            if to_load:
                template_data.update(
                    load_templates(
                        to_load, template_loads[0], template_loads[1]
                    )
                )
                self.update_load_state(data_type, to_load, name)

        return template_data

    def add_template_dirs(
        self,
        dir_paths: List[str],
        rel_path: str = ".",
        name: str = ROOT_NAMESPACE,
        allow_dup: bool = False,
    ) -> int:
        """
        Add template directories, return the number of directories added.
        """

        return self.add_dirs(
            DataType.TEMPLATE, dir_paths, rel_path, name, allow_dup
        )
