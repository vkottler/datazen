# =====================================
# generator=datazen
# version=3.0.11
# hash=781d3be287b59fe3641155ab11f7eb9c
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
        "3.7",
        "3.8",
        "3.9",
        "3.10",
    ],
}
setup(
    pkg_info,
    author_info,
)
