#!/usr/bin/env python
import logging
import os
from importlib import util
from os import path

import setuptools
from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

logger = logging.getLogger(__name__)
spec = util.spec_from_file_location(
    "checkov.version", os.path.join("checkov", "version.py")
)
# noinspection PyUnresolvedReferences
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore
version = mod.version  # type: ignore

setup(
    extras_require={
        "dev": [
            "alabaster==0.7.12",
            "attrs==19.3.0",
            "babel==2.7.0",
            "certifi==2019.11.28",
            "chardet==3.0.4",
            "coverage==4.5.4",
            "coverage-badge==1.0.1",
            "docopt==0.6.2",
            "docutils==0.15.2",
            "idna==2.8",
            "imagesize==1.1.0",
            "importlib-metadata==1.1.0; python_version < '3.8'",
            "jinja2==2.10.3",
            "lark-parser==0.7.8",
            "markupsafe==1.1.1",
            "more-itertools==8.0.0",
            "packaging==19.2",
            "pluggy==0.13.1",
            "py==1.8.0",
            "pygments==2.5.2",
            "pyparsing==2.4.5",
            "pytest==5.3.1",
            "bc-python-hcl2>=0.3.10",
            "pytz==2019.3",
            "pyyaml==5.3.1",
            "requests==2.22.0",
            "six==1.15.0",
            "snowballstemmer==2.0.0",
            "sphinx==2.2.1",
            "sphinxcontrib-applehelp==1.0.1",
            "sphinxcontrib-devhelp==1.0.1",
            "sphinxcontrib-htmlhelp==1.0.2",
            "sphinxcontrib-jsmath==1.0.1",
            "sphinxcontrib-qthelp==1.0.2",
            "sphinxcontrib-serializinghtml==1.1.3",
            "urllib3==1.25.10",
            "wcwidth==0.1.7",
            "zipp==0.6.0",
            "GitPython==3.1.7",
            "gitdb==4.0.5"
        ]
    },
    install_requires=[
        "update-checker==0.18.0",
        "tqdm==4.49.0",
        "boto3==1.12.43",
        "chardet==3.0.4",
        "colorama==0.4.3",
        "docopt==0.6.2",
        "idna==2.8",
        "jmespath==0.10.0",
        "junit-xml==1.8",
        "lark-parser==0.7.8",
        "bc-python-hcl2>=0.3.11",
        "pyyaml==5.3.1",
        "requests==2.22.0",
        "six==1.15.0",
        "tabulate==0.8.6",
        "termcolor==1.1.0",
        "urllib3==1.25.10",
        "dpath==1.5.0",
        "GitPython==3.1.7",
        "gitdb==4.0.5"
    ],
    license="Apache License 2.0",
    name="checkov",
    version=version,
    description="Infrastructure as code static analysis",
    author="bridgecrew",
    author_email="meet@bridgecrew.io",
    url="https://github.com/bridgecrewio/checkov",
    packages=setuptools.find_packages(exclude=["tests*","integration_tests*"]),
    scripts=["bin/checkov","bin/checkov.cmd"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.7',
        'Topic :: Security',
        'Topic :: Software Development :: Build Tools'
    ]
)
