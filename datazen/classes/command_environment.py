
"""
datazen - An environment extension that exposes command-line command execution.
"""

# built-in
import logging
from typing import List, Tuple

# internal
from datazen.classes.task_environment import TaskEnvironment

LOG = logging.getLogger(__name__)


class CommandEnvironment(TaskEnvironment):
    """ TODO """

    def __init__(self):
        """ Add the 'commands' handle. """

        super().__init__()
        self.handles["commands"] = self.valid_command

    def valid_command(self, entry: dict, namespace: str, dep_data: dict = None,
                      deps_changed: List[str] = None) -> Tuple[bool, bool]:
        """ Perform the command specified by the entry. """

        LOG.info(entry)
        LOG.info(namespace)
        LOG.info(dep_data)
        LOG.info(deps_changed)
        LOG.info(self.handles)

        return False, False
