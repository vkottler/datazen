# =====================================
# generator=datazen
# version=2.0.0
# hash=d52e072fd0dde737b3c3a09cbbfbb85c
# =====================================

"""
Useful defaults and other package metadata.
"""

DESCRIPTION = "Compile and render schema-validated configuration data."
PKG_NAME = "datazen"
VERSION = "2.0.0"

DEFAULT_TYPE = "yaml"
DEFAULT_MANIFEST = f"manifest.{DEFAULT_TYPE}"
DEFAULT_DIR = f"{PKG_NAME}-out"
DEFAULT_INDENT = 2
CACHE_SUFFIX = "_cache"
GLOBAL_KEY = "global"


def to_private(input_str: str) -> str:
    """Convert some input to a 'private' String."""

    return f"__{input_str}__"


ROOT_NAMESPACE = to_private("root")
