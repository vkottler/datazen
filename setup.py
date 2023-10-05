# =====================================
# generator=datazen
# version=3.1.4
# hash=3772d6d13c0e602fe7bb2cefab8f4ef5
# =====================================

"""
datazen - Package definition for distribution.
"""

# third-party
try:
    from setuptools_wrapper.setup import setup
except (ImportError, ModuleNotFoundError):
    from datazen_bootstrap.setup import setup  # type: ignore

# internal
from datazen import DESCRIPTION, PKG_NAME, VERSION

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
        "3.10",
        "3.11",
        "3.12",
    ],
}
setup(
    pkg_info,
    author_info,
)
