
"""
datazen - Package definition for distribution.
"""

# built-in
import os

# third-party
import setuptools  # type: ignore

# internal
from datazen import PKG_NAME, VERSION, DESCRIPTION


# get long description
with open("README.md", "r") as desc_file:
    long_description = desc_file.read()

# get requirements
with open("requirements.txt", "r") as reqs_file:
    reqs = reqs_file.read().strip().split()

# get data files
data_files = []
for root, _, files in os.walk(os.path.join(PKG_NAME, "data")):
    for fname in files:
        rel_name = os.path.join(root, fname).replace(PKG_NAME + os.sep, "")
        data_files.append(rel_name)

setuptools.setup(
    name=PKG_NAME,
    version=VERSION,
    author="Vaughn Kottler",
    author_email="vaughnkottler@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vkottler/{}".format(PKG_NAME),
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["dz=datazen.entry:main"]},
    install_requires=reqs,
    package_data={PKG_NAME: data_files},
)
