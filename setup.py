# =====================================
# generator=datazen
# version=1.7.2
# hash=a0de9ff3beb63c03b085d7de51150849
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
