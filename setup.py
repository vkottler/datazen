# =====================================
# generator=datazen
# version=1.9.1
# hash=51648ade369be925756decfbfe8497ec
# =====================================

"""
datazen - Package definition for distribution.
"""

# third-party
try:
    from vmklib.setup import setup
except ImportError:
    from vmklib_bootstrap.setup import setup  # type: ignore

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
    ],
}
setup(
    pkg_info,
    author_info,
    entry_override="dz",
)
