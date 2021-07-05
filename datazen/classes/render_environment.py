"""
datazen - An environment extension that exposes rendering capabilities.
"""

# built-in
import logging
import os
from typing import List, Tuple, Optional

# third-party
import jinja2

# internal
from datazen import GLOBAL_KEY
from datazen.classes.base_environment import dep_slug_unwrap
from datazen.classes.task_environment import TaskEnvironment, get_path
from datazen.fingerprinting import build_fingerprint
from datazen.paths import get_file_ext
from datazen.targets import resolve_dep_data

LOG = logging.getLogger(__name__)


def render_name_to_key(name: str) -> str:
    """Convert the name of a render target with a valid dictionary key."""

    return name.replace(".", "_")


def indent_str(data: str, indent: int, sep: str = os.linesep) -> str:
    """
    Attempt to indent String data by some amount, based on some separator.
    """

    result = ""
    ind_str = " " * indent
    for line in data.split(sep):
        if line:
            result += ind_str + line + sep
        else:
            result += sep
    return result.rstrip()


def get_render_str(
    template: jinja2.Template,
    name: str,
    indent: int,
    data: dict = None,
    out_data: dict = None,
) -> str:
    """Render a template."""

    # add a self-reference key for convenience
    global_added: bool = False
    if data is not None and GLOBAL_KEY not in data:
        data[GLOBAL_KEY] = data
        global_added = True

    result = template.render(data).rstrip()

    if global_added:
        assert data is not None
        del data[GLOBAL_KEY]

    # add indents if requested
    result = indent_str(result, indent)

    if out_data is not None:
        out_data[render_name_to_key(name)] = result
    return result


def get_render_children(
    children: dict,
    dep_data: dict,
    default_op: str,
    indent: int,
    delimeter: str = "",
) -> None:
    """Build child dependency data."""

    result = []
    for child in children:
        slug = dep_slug_unwrap(child, default_op)
        assert slug[1] in dep_data
        assert isinstance(dep_data[slug[1]], str)
        result.append(dep_data[slug[1]])
    dep_data["__children__"] = indent_str(delimeter.join(result), indent)


class RenderEnvironment(TaskEnvironment):
    """Leverages a cache-equipped environment to render templates."""

    def __init__(self):
        """Add the 'renders' handle."""

        super().__init__()
        self.handles["renders"] = self.valid_render

    def perform_render(
        self,
        template: jinja2.Template,
        path: Optional[str],
        entry: dict,
        data: dict = None,
    ) -> Tuple[bool, bool]:
        """
        Render a template to the requested path using the provided data.
        """

        try:
            out_data: dict = {}
            render_str = get_render_str(
                template, entry["name"], entry["indent"], data, out_data
            )

            # determine if the caller wanted a dynamic fingerprint or not,
            # if an indent is set, also disable it
            dynamic = True
            if (
                "no_dynamic_fingerprint" in entry
                and entry["no_dynamic_fingerprint"]
            ) or entry["indent"]:
                dynamic = False

            fprint = build_fingerprint(
                render_str, get_file_ext(get_path(entry)), dynamic=dynamic
            )

            # don't write a file, if requested
            if path is not None:
                with open(path, "w") as render_out:
                    render_out.write(fprint + render_str + os.linesep)
                os.sync()

            # save the output into a dict for consistency
            self.store_render(entry, out_data)
        except jinja2.exceptions.TemplateError as exc:
            LOG.error(
                "couldn't render '%s' to '%s': %s", entry["name"], path, exc
            )
            return False, False

        LOG.info("(%s) rendered '%s'", entry["name"], path)

        return True, True

    def store_render(self, entry: dict, data: dict) -> None:
        """Store data from the current render."""

        if "as" in entry and entry["as"]:
            name_key = render_name_to_key(entry["name"])
            data[entry["as"]] = data[name_key]
            if entry["as"] != name_key:
                del data[name_key]
        self.task_data["renders"][entry["name"]] = data

    def valid_render(
        self,
        entry: dict,
        namespace: str,
        dep_data: dict = None,
        deps_changed: List[str] = None,
    ) -> Tuple[bool, bool]:
        """Perform the render specified by the entry."""

        # determine the output that will be produced
        path = None
        if "no_file" not in entry or not entry["no_file"]:
            path = get_path(entry)

        if "indent" not in entry:
            entry["indent"] = 0

        # load templates
        templates = self.cached_load_templates(namespace)

        temp_name = entry["name"]
        if "key" in entry and entry["key"]:
            temp_name = entry["key"]

        if temp_name not in templates:
            LOG.error(
                "no template for key '%s' found, options: %s",
                entry["name"],
                list(templates.keys()),
            )
            return False, False

        template = templates[temp_name]

        # if dependencies aren't specified, use config data (but don't allow
        # an implicit 'compile')
        change_criteria = ["templates"]
        if not dep_data and "dependencies" not in entry:
            dep_data = self.cached_load_configs(namespace)
            change_criteria.append("configs")
            LOG.debug(
                "no dependencies loaded for '%s', using config data",
                entry["name"],
            )

        # apply overrides if present
        if dep_data is not None:
            dep_data = resolve_dep_data(entry, dep_data)

        if "children" in entry:
            assert dep_data is not None
            get_render_children(
                entry["children"],
                dep_data,
                self.default,
                entry.get("child_indent", 0),
                entry.get("child_delimeter", ""),
            )

        # determine if we need to perform this render
        assert template.filename is not None
        load_checks = {"templates": [template.filename]}
        if self.already_satisfied(
            entry["name"], path, change_criteria, deps_changed, load_checks
        ):
            LOG.debug("render '%s' satisfied, skipping", entry["name"])
            return True, False

        return self.perform_render(template, path, entry, dep_data)
