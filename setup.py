# =====================================
# generator=datazen
# version=1.0.10
# hash=0fa1178d9540f58f50fa175c79123a54
# =====================================

"""
datazen - Package definition for distribution.
"""

# internal
from datazen import PKG_NAME, VERSION, DESCRIPTION
from mk.setup import setup


author_info = {"name": "Vaughn Kottler",
               "email": "vaughnkottler@gmail.com",
               "username": "vkottler"}
pkg_info = {"name": PKG_NAME, "version": VERSION, "description": DESCRIPTION}
setup(
    pkg_info,
    author_info,
    entry_override="dz",
)
