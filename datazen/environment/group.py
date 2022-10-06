"""
datazen - A target-type for grouping other target-tasks together.
"""

# built-in
import logging
from typing import List

# third-party
from vcorelib.dict import GenericStrDict

# internal
from datazen.environment.base import TaskResult
from datazen.environment.task import TaskEnvironment


class GroupEnvironment(TaskEnvironment):
    """Leverages a task-environment to group tasks together."""

    def __init__(self, **kwargs):
        """Add the 'renders' handle."""

        super().__init__(**kwargs)
        self.handles["groups"] = self.valid_group

    def valid_group(
        self,
        entry: GenericStrDict,
        _: str,
        dep_data: GenericStrDict = None,
        deps_changed: List[str] = None,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> TaskResult:
        """Stub task to group other tasks."""

        if dep_data is not None:
            self.task_data["groups"][entry["name"]] = dep_data
        changed = bool(deps_changed)
        if changed:
            logger.info("group '%s' updated", entry["name"])
        return TaskResult(True, changed)
