"""
datazen - An environment extension that exposes command-line command execution.
"""

# built-in
from collections import defaultdict
import logging
import os
import subprocess
from typing import List

# internal
from datazen.environment.base import TaskResult
from datazen.environment.task import TaskEnvironment, get_path


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
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> TaskResult:
        """Perform the command specified by the entry."""

        cmd = [entry["command"]]
        if "arguments" in entry and entry["arguments"]:
            cmd += entry["arguments"]

        if entry["name"] not in self.task_data["commands"]:
            self.task_data["commands"][entry["name"]] = {}
        task_data = self.task_data["commands"][entry["name"]]

        # determine if the command needs to run
        file_exists = True
        if "file" in entry:
            file_exists = os.path.isfile(get_path(entry, "file"))
        force = "force" in entry and entry["force"]
        if not force and (
            not deps_changed and file_exists and entry["name"] in task_data
        ):
            return TaskResult(True, False)

        result = subprocess.run(cmd, capture_output=True)

        task_data[entry["name"]] = defaultdict(str)
        data = task_data[entry["name"]]
        data["args"] = result.args
        data["stdout"] = result.stdout.decode()
        data["stderr"] = result.stderr.decode()
        data["returncode"] = str(result.returncode)

        # log information about failures
        if result.returncode != 0:
            logger.error("command '%s' failed!", entry["command"])
            logger.error("args: %s", ", ".join(result.args))
            logger.error("exit: %d", result.returncode)
            logger.error("stdout:")
            print(data["stdout"])
            logger.error("stderr:")
            print(data["stderr"])

        return TaskResult(result.returncode == 0, True)
