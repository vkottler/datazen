# =====================================
# generator=datazen
# version=3.1.1
# hash=58d450b1b8ac664ad4c76e5b568cf91f
# =====================================

"""
Useful defaults and other package metadata.
"""

DESCRIPTION = "Compile and render schema-validated configuration data."
PKG_NAME = "datazen"
VERSION = "3.1.2"

# datazen-specific content.
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
