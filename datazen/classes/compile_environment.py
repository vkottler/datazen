"""
datazen - An environment extension that exposes compilation capabilities.
"""

# built-in
import logging
import os
from typing import List, Tuple

# internal
from datazen.classes.task_environment import TaskEnvironment
from datazen.compile import str_compile, get_compile_output
from datazen.paths import advance_dict_by_path
from datazen.targets import resolve_dep_data

LOG = logging.getLogger(__name__)


class CompileEnvironment(TaskEnvironment):
    """Leverages a cache-equipped environment to perform compilations."""

    def __init__(self):
        """
        Add compiled data to a dictionary whenever a compilation is performed.
        """

        super().__init__()
        self.handles["compiles"] = self.valid_compile

    def valid_compile(
        self,
        entry: dict,
        namespace: str,
        dep_data: dict = None,
        deps_changed: List[str] = None,
    ) -> Tuple[bool, bool]:
        """Perform the compilation specified by the entry."""

        path, output_type = get_compile_output(entry)

        # load configs early to update cache
        data = self.cached_load_configs(namespace)

        # update this dict with the dependency data
        if dep_data is not None:
            data.update(dep_data)

        # advance the dict if it was requested
        if "index_path" in entry:
            data = advance_dict_by_path(entry["index_path"].split("."), data)

        # apply overrides if present
        data = resolve_dep_data(entry, data)

        # set task-data early, in case we don't need to re-compile
        self.task_data["compiles"][entry["name"]] = data

        # make sure this compilation needs to be performed
        if self.already_satisfied(
            entry["name"],
            path,
            ["configs", "variables", "schemas"],
            deps_changed,
        ):
            LOG.debug("compile '%s' satisfied, skipping", entry["name"])
            return True, False

        mode = "a" if "append" in entry and entry["append"] else "w"
        with open(path, mode) as out_file:
            out_file.write(str_compile(data, output_type))
            LOG.info("compiled '%s' data to '%s'", output_type, path)
        os.sync()

        return True, True
