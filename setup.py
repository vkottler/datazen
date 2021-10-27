# =====================================
# generator=datazen
# version=1.9.0
# hash=d6879e4f3695c6a5760442c423e11c7a
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
    "slug": PKG_NAME.replace("-", "_"),
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
