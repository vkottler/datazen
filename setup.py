# =====================================
# generator=datazen
# version=1.1.0
# hash=97839a45590a9ddf01d3ac75e8e911d4
# =====================================

"""
datazen - Package definition for distribution.
"""

# internal
from datazen import PKG_NAME, VERSION, DESCRIPTION

# third-party
from vmklib.setup import setup


author_info = {"name": "Vaughn Kottler",
               "email": "vaughnkottler@gmail.com",
               "username": "vkottler"}
pkg_info = {"name": PKG_NAME, "version": VERSION, "description": DESCRIPTION}
setup(
    pkg_info,
    author_info,
    entry_override="dz",
)
