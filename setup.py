# =====================================
# generator=datazen
# version=1.3.0
# hash=5c7e9660ab8e4c2d1c03184fdda5f9f6
# =====================================

"""
datazen - Package definition for distribution.
"""

# third-party
from vmklib.setup import setup  # type: ignore

# internal
from datazen import PKG_NAME, VERSION, DESCRIPTION


author_info = {"name": "Vaughn Kottler",
               "email": "vaughnkottler@gmail.com",
               "username": "vkottler"}
pkg_info = {"name": PKG_NAME, "version": VERSION, "description": DESCRIPTION}
setup(
    pkg_info,
    author_info,
    entry_override="dz",
)
