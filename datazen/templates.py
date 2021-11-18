"""
datazen - Top-level APIs for loading and interacting with templates.
"""

# built-in
import os
from typing import Dict, List

# third-party
import jinja2

# internal
from datazen.load import DEFAULT_LOADS, LoadedFiles
from datazen.parsing import set_file_hash
from datazen.paths import get_file_ext, get_file_name


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


def load(
    template_dirs: List[str],
    loads: LoadedFiles = DEFAULT_LOADS,
) -> Dict[str, jinja2.Template]:
    """
    Load jinja2 templates from a list of directories where templates can be
    found.
    """

    result = {}

    # setup jinja environment
    loader = jinja2.FileSystemLoader(template_dirs, followlinks=True)
    env = jinja2.Environment(
        loader=loader, trim_blocks=True, lstrip_blocks=True
    )

    # manually inspect directories to write into the cache
    for template_dir in template_dirs:
        update_cache_primitives(template_dir, loads)

    # load templates into a dictionary
    for template in env.list_templates():
        key = get_file_name(template)
        assert get_file_ext(template) == "j2"
        result[key] = env.get_template(template)
    return result
