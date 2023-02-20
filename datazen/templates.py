"""
datazen - Top-level APIs for loading and interacting with templates.
"""

# built-in
import os
from typing import Dict, Iterable, Type

# third-party
import jinja2
from vcorelib.dict import GenericStrDict
from vcorelib.paths import Pathlike, get_file_ext, get_file_name, normalize

# internal
from datazen.load import DEFAULT_LOADS, LoadedFiles
from datazen.parsing import set_file_hash


def update_cache_primitives(dir_path: str, loads: LoadedFiles) -> None:
    """
    From a directory path, update the 'loaded_list' and 'hashes' primitives
    that belong to an upstream cache.
    """

    for path in os.listdir(dir_path):
        fpath = os.path.abspath(os.path.join(dir_path, path))
        if os.path.isfile(fpath):
            if loads.file_data is not None:
                if set_file_hash(loads.file_data, fpath):
                    assert loads.files is not None
                    loads.files.append(fpath)


def environment(
    auto_reload: bool = False,
    autoescape_kwargs: GenericStrDict = None,
    lstrip_blocks: bool = True,
    trim_blocks: bool = True,
    undefined: Type[jinja2.Undefined] = jinja2.StrictUndefined,
    **kwargs,
) -> jinja2.Environment:
    """Create a jinja environment with some sane defaults."""

    if autoescape_kwargs is None:
        autoescape_kwargs = {}

    return jinja2.Environment(
        auto_reload=auto_reload,
        autoescape=jinja2.select_autoescape(**autoescape_kwargs),
        lstrip_blocks=lstrip_blocks,
        trim_blocks=trim_blocks,
        undefined=undefined,
        **kwargs,
    )


def load(
    template_dirs: Iterable[Pathlike],
    loads: LoadedFiles = DEFAULT_LOADS,
) -> Dict[str, jinja2.Template]:
    """
    Load jinja2 templates from a list of directories where templates can be
    found.
    """

    templates = [str(normalize(x)) for x in template_dirs]

    # Setup jinja environment.
    env = environment(
        loader=jinja2.FileSystemLoader(templates, followlinks=True)
    )

    # Manually inspect directories to write into the cache.
    for template_dir in templates:
        update_cache_primitives(template_dir, loads)

    # Load templates into a dictionary.
    result = {}
    for template in env.list_templates():
        key = get_file_name(template)
        assert get_file_ext(template) == "j2"
        result[key] = env.get_template(template)
    return result
