"""
datazen - A target-type for grouping other target-tasks together.
"""

# built-in
from typing import List, Tuple

# internal
from datazen.classes.task_environment import TaskEnvironment


class GroupEnvironment(TaskEnvironment):
    """Leverages a task-environment to group tasks together."""

    def __init__(self):
        """Add the 'renders' handle."""

        super().__init__()
        self.handles["groups"] = self.valid_group

    def valid_group(
        self,
        entry: dict,
        _: str,
        dep_data: dict = None,
        deps_changed: List[str] = None,
    ) -> Tuple[bool, bool]:
        """Stub task to group other tasks."""

        if dep_data is not None:
            self.task_data["groups"][entry["name"]] = dep_data
        return (True, bool(deps_changed))
