# =====================================
# generator=datazen
# version=1.3.1
# hash=6e5e88b7595af2c5ac6139147c115add
# =====================================

"""
datazen - Useful defaults and other package metadata.
"""

PKG_NAME = "datazen"
VERSION = "1.3.1"
DESCRIPTION = "Compile and render schema-validated configuration data."

DEFAULT_TYPE = "yaml"
DEFAULT_MANIFEST = "manifest.{}".format(DEFAULT_TYPE)
DEFAULT_DIR = "{}-out".format(PKG_NAME)
CACHE_SUFFIX = "_cache"
GLOBAL_KEY = "global"
ROOT_NAMESPACE = "__root__"
