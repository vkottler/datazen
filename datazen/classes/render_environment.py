
"""
datazen - An environment extension that exposes rendering capabilities.
"""

# built-in
import logging
import os
from typing import List, Tuple

# internal
from datazen.classes.task_environment import TaskEnvironment

LOG = logging.getLogger(__name__)


class RenderEnvironment(TaskEnvironment):
    """ Leverages a cache-equipped environment to render templates. """

    def __init__(self):
        """ Add the 'renders' handle. """

        super().__init__()
        self.handles["renders"] = self.valid_render

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
            LOG.error("no template for key '%s' found", entry["name"])
            return False, False

        # determine if we need to perform this render
        if self.already_satisfied(entry["name"], path, ["templates"],
                                  deps_changed):
            LOG.debug("render '%s' satisfied, skipping", entry["name"])
            return True, False

        # render the template
        with open(path, "w") as render_out:
            render_str = templates[entry["name"]].render(dep_data)
            render_out.write(render_str)

            # save the output into a dict for consistency
            self.task_data["renders"][entry["name"]] = render_str

        LOG.info("(%s) rendered '%s'", entry["name"], path)

        return True, True
