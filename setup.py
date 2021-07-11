# =====================================
# generator=datazen
# version=1.7.7
# hash=4c44954e68d21dfc2ef72a75abf168a6
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
    ],
}
setup(
    pkg_info,
    author_info,
    entry_override="dz",
)
