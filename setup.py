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
            "pytest==5.3.1",
            "coverage",
            "coverage-badge",
            "GitPython==3.1.7",
            "bandit"
        ]
    },
    install_requires=[
        "bc-python-hcl2>=0.3.18",
        "cloudsplaining>=0.4.1",
        "deep_merge",
        "tabulate",
        "colorama",
        "termcolor",
        "junit-xml",
        "dpath>=1.5.0,<2",
        "pyyaml>=5.4.1",
        "boto3==1.17.*",
        "GitPython",
        "six==1.15.0",
        "jmespath",
        "tqdm",
        "update_checker",
        "semantic_version",
        "packaging",
        "networkx",
        "dockerfile-parse",
        "docker",
        "configargparse"
    ],
    license="Apache License 2.0",
    name="checkov",
    version=version,
    python_requires=">=3.7",
    description="Infrastructure as code static analysis",
    author="bridgecrew",
    author_email="meet@bridgecrew.io",
    url="https://github.com/nimrodkor/checkov",
    packages=setuptools.find_packages(exclude=["tests*","integration_tests*"]),
    include_package_data=True,
    package_dir={'checkov.terraform.checks.graph_checks': 'checkov/terraform/checks/graph_checks'},
    package_data = {'checkov.terraform.checks.graph_checks': ['aws/*.yaml', 'gcp/*.yaml', 'azure/*.yaml']},
    scripts=["bin/checkov", "bin/checkov.cmd"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Security',
        'Topic :: Software Development :: Build Tools'
    ]
)
