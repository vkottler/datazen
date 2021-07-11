# =====================================
# generator=datazen
# version=1.7.7
# hash=4e5a2fa5864db550cb86433f0ce98c79
# =====================================

"""
datazen - Useful defaults and other package metadata.
"""

PKG_NAME = "datazen"
VERSION = "1.7.7"
DESCRIPTION = "Compile and render schema-validated configuration data."

DEFAULT_TYPE = "yaml"
DEFAULT_MANIFEST = "manifest.{}".format(DEFAULT_TYPE)
DEFAULT_DIR = "{}-out".format(PKG_NAME)
CACHE_SUFFIX = "_cache"
GLOBAL_KEY = "global"
ROOT_NAMESPACE = "__root__"
