# =====================================
# generator=datazen
# version=1.5.0
# hash=70ca23bd1611e082b11af0680e66ae30
# =====================================

"""
datazen - Useful defaults and other package metadata.
"""

PKG_NAME = "datazen"
VERSION = "1.5.1"
DESCRIPTION = "Compile and render schema-validated configuration data."

DEFAULT_TYPE = "yaml"
DEFAULT_MANIFEST = "manifest.{}".format(DEFAULT_TYPE)
DEFAULT_DIR = "{}-out".format(PKG_NAME)
CACHE_SUFFIX = "_cache"
GLOBAL_KEY = "global"
ROOT_NAMESPACE = "__root__"
