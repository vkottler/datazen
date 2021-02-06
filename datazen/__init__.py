# =====================================
# generator=datazen
# version=1.3.4
# hash=a0e9ed7886a8188f738647628ace13e7
# =====================================

"""
datazen - Useful defaults and other package metadata.
"""

PKG_NAME = "datazen"
VERSION = "1.3.5"
DESCRIPTION = "Compile and render schema-validated configuration data."

DEFAULT_TYPE = "yaml"
DEFAULT_MANIFEST = "manifest.{}".format(DEFAULT_TYPE)
DEFAULT_DIR = "{}-out".format(PKG_NAME)
CACHE_SUFFIX = "_cache"
GLOBAL_KEY = "global"
ROOT_NAMESPACE = "__root__"
