
"""
datazen - An environment extension that exposes command-line command execution.
"""

# built-in
from collections import defaultdict
import logging
import subprocess
from typing import Dict, List, Tuple

# internal
from datazen.classes.task_environment import TaskEnvironment

LOG = logging.getLogger(__name__)


class CommandEnvironment(TaskEnvironment):
    """ Exposes command-line commanding capability to the environment. """

    def __init__(self):
        """ Add the 'commands' handle. """

        super().__init__()
        self.handles["commands"] = self.valid_command

    def valid_command(self, entry: dict, _: str, __: dict = None,
                      ___: List[str] = None) -> Tuple[bool, bool]:
        """ Perform the command specified by the entry. """

        cmd = [entry["command"]]
        if "arguments" in entry and entry["arguments"]:
            cmd += entry["arguments"]

        result = subprocess.run(cmd, capture_output=True)

        cmd_data: Dict[str, Dict[str, str]] = {entry["name"]: defaultdict(str)}
        cmd_data[entry["name"]]["args"] = result.args
        cmd_data[entry["name"]]["stdout"] = result.stdout.decode()
        cmd_data[entry["name"]]["stderr"] = result.stderr.decode()
        cmd_data[entry["name"]]["returncode"] = str(result.returncode)
        self.task_data["commands"][entry["name"]] = cmd_data

        return result.returncode == 0, True
