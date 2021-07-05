"""
datazen - An environment extension that exposes command-line command execution.
"""

# built-in
from collections import defaultdict
import logging
import os
import subprocess
from typing import List, Tuple

# internal
from datazen.classes.task_environment import TaskEnvironment, get_path

LOG = logging.getLogger(__name__)


class CommandEnvironment(TaskEnvironment):
    """Exposes command-line commanding capability to the environment."""

    def __init__(self):
        """Add the 'commands' handle."""

        super().__init__()
        self.handles["commands"] = self.valid_command

    def valid_command(
        self,
        entry: dict,
        _: str,
        __: dict = None,
        deps_changed: List[str] = None,
    ) -> Tuple[bool, bool]:
        """Perform the command specified by the entry."""

        cmd = [entry["command"]]
        if "arguments" in entry and entry["arguments"]:
            cmd += entry["arguments"]

        task_data = self.task_data["commands"][entry["name"]]

        # determine if the command needs to run
        file_exists = True
        if "file" in entry:
            file_exists = os.path.isfile(get_path(entry, "file"))
        force = "force" in entry and entry["force"]
        if not force and (
            not deps_changed and file_exists and entry["name"] in task_data
        ):
            return True, False

        result = subprocess.run(cmd, capture_output=True)

        task_data[entry["name"]] = defaultdict(str)
        data = task_data[entry["name"]]
        data["args"] = result.args
        data["stdout"] = result.stdout.decode()
        data["stderr"] = result.stderr.decode()
        data["returncode"] = str(result.returncode)

        # log information about failures
        if result.returncode != 0:
            LOG.error("command '%s' failed!", entry["command"])
            LOG.error("args: %s", ", ".join(result.args))
            LOG.error("exit: %d", result.returncode)
            LOG.error("stdout:")
            print(data["stdout"])
            LOG.error("stderr:")
            print(data["stderr"])

        return result.returncode == 0, True
