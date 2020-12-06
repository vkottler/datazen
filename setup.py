
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
