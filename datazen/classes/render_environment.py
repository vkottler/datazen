
"""
datazen - An environment extension that exposes rendering capabilities.
"""

# built-in
import logging

# internal
from datazen.classes.task_environment import TaskEnvironment

LOG = logging.getLogger(__name__)


class RenderEnvironment(TaskEnvironment):
    """ Leverages a cache-equipped environment to render templates. """

    def __init__(self):
        """ TODO """

        super().__init__()
        self.handles["renders"] = self.valid_render

    def valid_render(self, render_entry: dict, namespace: str,
                     dep_data: dict = None) -> bool:
        """ Perform the render specified by the entry. """

        LOG.info(self.manifest["path"])
        LOG.info(render_entry)
        LOG.info(namespace)
        LOG.info(dep_data)

        return True
