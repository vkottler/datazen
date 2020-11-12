
"""
datazen - Top-level APIs for loading and interacting with templates.
"""

# built-in
import os
from typing import Dict, List

# third-party
import jinja2

# internal
from datazen.paths import get_file_name, get_file_ext
from datazen.parsing import get_file_hash


def update_cache_primitives(dir_path: str, loaded_list: List[str],
                            hashes: Dict[str, str]) -> None:
    """
    From a directory path, update the 'loaded_list' and 'hashes' primitives
    that belong to an upstream cache.
    """

    for path in os.listdir(dir_path):
        file_path = os.path.abspath(os.path.join(dir_path, path))
        if os.path.isfile(file_path):
            str_hash = get_file_hash(file_path)
            if file_path not in hashes or hashes[file_path] != str_hash:
                loaded_list.append(file_path)
            hashes[file_path] = str_hash


def load(template_dirs: List[str], loaded_list: List[str] = None,
         hashes: Dict[str, str] = None) -> Dict[str, jinja2.Template]:
    """
    Load jinja2 templates from a list of directories where templates can be
    found.
    """

    result = {}

    # setup jinja environment
    loader = jinja2.FileSystemLoader(template_dirs, followlinks=True)
    env = jinja2.Environment(loader=loader, trim_blocks=True,
                             lstrip_blocks=True)

    # manually inspect directories to write into the cache
    if hashes is not None and loaded_list is not None:
        for template_dir in template_dirs:
            update_cache_primitives(template_dir, loaded_list, hashes)

    # load templates into a dictionary
    for template in env.list_templates():
        key = get_file_name(template)
        assert get_file_ext(template) == "j2"
        result[key] = env.get_template(template)
    return result
