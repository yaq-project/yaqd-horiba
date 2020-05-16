#! /usr/bin/env python3
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(fname):
    return open(os.path.join(here, fname)).read()


with open(os.path.join(here, "yaqd_horiba", "VERSION")) as version_file:
    version = version_file.read().strip()

with open("README.md") as readme_file:
    readme = readme_file.read()


extra_files = {"yaqd_horiba": ["VERSION"]}

setup(
    name="yaqd-horiba",
    packages=find_packages(exclude=("tests", "tests.*")),
    package_data=extra_files,
    python_requires=">=3.7",
    install_requires=["yaqd-core>=2020.05.1", "pyusb"],
    extras_require={
        "docs": ["sphinx", "sphinx-gallery>=0.3.0", "sphinx-rtd-theme"],
        "dev": ["black", "pre-commit", "pydocstyle"],
    },
    version=version,
    description="Yaq daemons for Horiba Jobin Yvon hardware",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="yaq Developers",
    license="LGPL v3",
    url="http://gitlab.com/yaq/yaqd-horiba",
    project_urls={
        "Source": "https://gitlab.com/yaq/yaqd-horiba",
        "Documentation": "https://yaq.fyi",
        "Issue Tracker": "https://gitlab.com/yaq/yaqd-horiba/issues",
    },
    entry_points={"console_scripts": ["yaqd-micro-hr=yaqd_horiba._microhr:MicroHR.main"]},
    keywords="spectroscopy science multidimensional hardware",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
)
