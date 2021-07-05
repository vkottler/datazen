# =====================================
# generator=datazen
# version=1.7.4
# hash=9dc35f14d1f79c1f1945aba334cefcd3
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
pkg_info = {"name": PKG_NAME, "version": VERSION, "description": DESCRIPTION}
setup(
    pkg_info,
    author_info,
    entry_override="dz",
)
