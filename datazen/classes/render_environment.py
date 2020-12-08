
"""
datazen - An environment extension that exposes rendering capabilities.
"""

# built-in
import logging
import os
from typing import List, Tuple

# third-party
import jinja2

# internal
from datazen.classes.task_environment import TaskEnvironment
from datazen.fingerprinting import build_fingerprint
from datazen.paths import get_file_ext

LOG = logging.getLogger(__name__)


class RenderEnvironment(TaskEnvironment):
    """ Leverages a cache-equipped environment to render templates. """

    def __init__(self):
        """ Add the 'renders' handle. """

        super().__init__()
        self.handles["renders"] = self.valid_render

    def perform_render(self, template: jinja2.Template,
                       path: str, entry: dict,
                       data: dict = None) -> Tuple[bool, bool]:
        """
        Render a template to the requested path using the provided data.
        """

        try:
            render_str = template.render(data).rstrip()
            render_str += os.linesep

            # determine if the caller wanted a dynamic fingerprint or not
            dynamic = True
            if ("no_dynamic_fingerprint" in entry and
                    entry["no_dynamic_fingerprint"]):
                dynamic = False

            fprint = build_fingerprint(render_str, get_file_ext(path),
                                       dynamic=dynamic)
            render_str = fprint + render_str
            with open(path, "w") as render_out:
                render_out.write(render_str)

            # save the output into a dict for consistency
            self.task_data["renders"][entry["name"]] = render_str
        except jinja2.exceptions.TemplateError as exc:
            LOG.error("couldn't render '%s' to '%s': %s",
                      entry["name"], path, exc)
            return False, False

        LOG.info("(%s) rendered '%s'", entry["name"], path)

        return True, True

    def valid_render(self, entry: dict, namespace: str, dep_data: dict = None,
                     deps_changed: List[str] = None) -> Tuple[bool, bool]:
        """ Perform the render specified by the entry. """

        # determine the output that will be produced
        path = entry["name"]
        if "output_path" in entry:
            path = entry["output_path"]
        path = os.path.join(entry["output_dir"], path)

        # load templates
        templates = self.cached_load_templates(namespace)

        if entry["name"] not in templates:
            LOG.error("no template for key '%s' found, options: %s",
                      entry["name"], list(templates.keys()))
            return False, False

        template = templates[entry["name"]]

        # if dependencies aren't specified, use config data (but don't allow
        # an implicit 'compile')
        change_criteria = ["templates"]
        if not dep_data and "dependencies" not in entry:
            dep_data = self.cached_load_configs(namespace)
            change_criteria.append("configs")
            LOG.debug("no dependencies loaded for '%s', using config data",
                      entry["name"])

        # determine if we need to perform this render
        assert template.filename is not None
        load_checks = {"templates": [template.filename]}
        if self.already_satisfied(entry["name"], path, change_criteria,
                                  deps_changed, load_checks):
            LOG.debug("render '%s' satisfied, skipping", entry["name"])
            return True, False

        return self.perform_render(template, path, entry, dep_data)
