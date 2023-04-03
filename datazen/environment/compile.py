"""
datazen - An environment extension that exposes compilation capabilities.
"""

# built-in
import logging
from typing import List

# third-party
from vcorelib.dict import GenericStrDict, merge_dicts
from vcorelib.paths import rel

# internal
from datazen.compile import get_compile_output, str_compile
from datazen.environment.base import TaskResult
from datazen.environment.task import TaskEnvironment
from datazen.paths import advance_dict_by_path
from datazen.targets import resolve_dep_data

LOG = logging.getLogger(__name__)


class CompileEnvironment(TaskEnvironment):
    """Leverages a cache-equipped environment to perform compilations."""

    def __init__(self, **kwargs) -> None:
        """
        Add compiled data to a dictionary whenever a compilation is performed.
        """

        super().__init__(**kwargs)
        self.handles["compiles"] = self.valid_compile

    def valid_compile(
        self,
        entry: GenericStrDict,
        namespace: str,
        dep_data: GenericStrDict = None,
        deps_changed: List[str] = None,
        logger: logging.Logger = LOG,
    ) -> TaskResult:
        """Perform the compilation specified by the entry."""

        path, output_type = get_compile_output(entry)

        # load configs early to update cache, only enforce schemas if we don't
        # have any dependency data to resolve
        data: GenericStrDict
        data, success, _ = self.cached_load_configs(
            name=namespace, enforce_schemas=dep_data is None
        )
        if not success:
            return TaskResult(False, False)

        # update this dict with the dependency data
        if dep_data is not None:
            # don't write compile-task-specific data into the dictionary
            # containing the underlying, loaded data
            data = data.copy()

            if entry.get("merge_deps", False):
                data = merge_dicts([data, dep_data], logger=logger)

            # this isn't a good default behavior in practice, but older code
            # (and tests) rely on it
            else:
                data.update(dep_data)

            # run schema validation now that all loaded data can be considered
            if not self.cached_enforce_schemas(data, name=namespace):
                logger.error("schema validation on merged config data failed")
                return TaskResult(False, False)

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
                data = data.get(str(entry["key"]), {})
            out_file.write(str_compile(data, output_type))
            logger.info("compiled '%s' data to '%s'", output_type, rel(path))

        return TaskResult(True, True)
