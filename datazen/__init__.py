# =====================================
# generator=datazen
# version=1.6.5
# hash=36aaa88c019b3bc22da2614b40844c57
# =====================================

"""
datazen - Useful defaults and other package metadata.
"""

PKG_NAME = "datazen"
VERSION = "1.6.6"
DESCRIPTION = "Compile and render schema-validated configuration data."

DEFAULT_TYPE = "yaml"
DEFAULT_MANIFEST = "manifest.{}".format(DEFAULT_TYPE)
DEFAULT_DIR = "{}-out".format(PKG_NAME)
CACHE_SUFFIX = "_cache"
GLOBAL_KEY = "global"
ROOT_NAMESPACE = "__root__"
