"""
datazen - An environment extension that exposes command-line command execution.
"""

# built-in
from collections import defaultdict
import logging
import os
import subprocess
from typing import List

# third-party
from vcorelib.dict import GenericStrDict
from vcorelib.logging import log_time
from vcorelib.task.subprocess.run import is_windows, reconcile_platform

# internal
from datazen.environment.base import TaskResult
from datazen.environment.task import TaskEnvironment, get_path

LOG = logging.getLogger(__name__)


class CommandEnvironment(TaskEnvironment):
    """Exposes command-line commanding capability to the environment."""

    def __init__(self, **kwargs) -> None:
        """Add the 'commands' handle."""

        super().__init__(**kwargs)
        self.handles["commands"] = self.valid_command

    def valid_command(
        self,
        entry: GenericStrDict,
        _: str,
        __: GenericStrDict = None,
        deps_changed: List[str] = None,
        logger: logging.Logger = LOG,
    ) -> TaskResult:
        """Perform the command specified by the entry."""

        cmd = []
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

        program = entry["command"]

        # Try and fix a path to a virtual-environment script on Windows.
        program = (
            program.replace("/bin/", "/Scripts/")
            if is_windows() and "venv" in program
            else program
        )

        # Try and fix a path to a program on Windows.
        program = program.replace("/", "\\") if is_windows() else program

        program, args = reconcile_platform(program, cmd)
        with log_time(logger, "Running '%s' with args: %s.", program, args):
            result = subprocess.run([program] + args, capture_output=True)

        task_data[entry["name"]] = defaultdict(str)
        data = task_data[entry["name"]]
        data["args"] = result.args

        stdout = result.stdout.decode()
        stderr = result.stderr.decode()

        # Fix newlines based on our newline argument.
        if entry.get("replace_newlines", True):
            stdout = stdout.replace(os.linesep, self.newline)
            stderr = stderr.replace(os.linesep, self.newline)

        data["stdout"] = stdout
        data["stderr"] = stderr
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
