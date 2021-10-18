# =====================================
# generator=datazen
# version=1.8.3
# hash=41d8433c7260b7057e0963d910f4f3d2
# =====================================

"""
datazen - Useful defaults and other package metadata.
"""

PKG_NAME = "datazen"
VERSION = "1.8.4"
DESCRIPTION = "Compile and render schema-validated configuration data."

DEFAULT_TYPE = "yaml"
DEFAULT_MANIFEST = f"manifest.{DEFAULT_TYPE}"
DEFAULT_DIR = f"{PKG_NAME}-out"
CACHE_SUFFIX = "_cache"
GLOBAL_KEY = "global"


def to_private(input_str: str) -> str:
    """Convert some input to a 'private' String."""

    return f"__{input_str}__"


ROOT_NAMESPACE = to_private("root")
