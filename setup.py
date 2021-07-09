# =====================================
# generator=datazen
# version=1.7.7
# hash=e26de6e5796a2d81910d13efa8008f08
# =====================================

"""
datazen - Package definition for distribution.
"""

# third-party
from vmklib.setup import setup

# internal
from datazen import PKG_NAME, VERSION, DESCRIPTION


author_info = {
    "name": "Vaughn Kottler",
    "email": "vaughnkottler@gmail.com",
    "username": "vkottler",
}
pkg_info = {
    "name": PKG_NAME,
    "version": VERSION,
    "description": DESCRIPTION,
    "versions": [
        "3.7",
        "3.8",
        "3.9",
    ],
}
setup(
    pkg_info,
    author_info,
    entry_override="dz",
)
