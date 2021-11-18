"""
datazen - An environment extension that exposes compilation capabilities.
"""

# built-in
import logging
from typing import List

# internal
from datazen.compile import get_compile_output, str_compile
from datazen.environment.base import TaskResult
from datazen.environment.task import TaskEnvironment
from datazen.parsing import merge_dicts
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
        logger: logging.Logger = LOG,
    ) -> TaskResult:
        """Perform the compilation specified by the entry."""

        path, output_type = get_compile_output(entry)

        # load configs early to update cache
        data = self.cached_load_configs(namespace)

        # update this dict with the dependency data
        if dep_data is not None:
            if entry.get("merge_deps", False):
                data = merge_dicts([data, dep_data], logger=logger)

            # this isn't a good default behavior in practice, but older code
            # (and tests) rely on it
            else:
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
            logger.debug("compile '%s' satisfied, skipping", entry["name"])
            return TaskResult(True, False)

        mode = "a" if "append" in entry and entry["append"] else "w"
        with open(path, mode, encoding="utf-8") as out_file:
            if "key" in entry:
                data = data.get(entry["key"], {})
            out_file.write(str_compile(data, output_type))
            logger.info("compiled '%s' data to '%s'", output_type, path)

        return TaskResult(True, True)
