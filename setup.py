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
            "coverage==5.5",
            "coverage-badge",
            "GitPython==3.1.7",
            "bandit",
            "jsonschema",
        ]
    },
    install_requires=[
        "bc-python-hcl2==0.3.47",
        "bc-detect-secrets==1.3.13",
        "deep-merge",
        "tabulate",
        "colorama",
        "termcolor<=2.0.1",
        "junit-xml>=1.9",
        "dpath<2,>=1.5.0",
        "pyyaml>=5.4.1",
        "boto3>=1.17",
        "gitpython",
        "jmespath",
        "tqdm",
        "update-checker",
        "semantic-version",
        "packaging",
        "cloudsplaining>=0.4.3",
        "networkx<2.7",
        "dockerfile-parse",
        "docker",
        "configargparse",
        "argcomplete",
        "policyuniverse",
        "typing-extensions>=4.1.0",
        "importlib-metadata>=0.12",
        "cachetools",
        "cyclonedx-python-lib>=2.4.0,<4.0.0",
        "packageurl-python",
        "click>=8.0.0",
        "aiohttp",
        "aiodns",
        "aiomultiprocess",
        "jsonpath-ng",
        "jsonschema<4.0.0,>=3.0.2",
        "prettytable>=3.0.0",
        "pycep-parser==0.3.9",
        "charset-normalizer",
        "pyston-autoload==2.3.5; python_version < '3.11' and (sys_platform == 'linux' or sys_platform == 'darwin') and platform_machine == 'x86_64'",
        "pyston==2.3.5; python_version < '3.11' and (sys_platform == 'linux' or sys_platform == 'darwin') and platform_machine == 'x86_64'",
        "schema",
    ],
    dependency_links=[],  # keep it empty, needed for pipenv-setup
    license="Apache License 2.0",
    name="checkov",
    version=version,
    python_requires=">=3.7",
    description="Infrastructure as code static analysis",
    author="bridgecrew",
    author_email="meet@bridgecrew.io",
    url="https://github.com/bridgecrewio/checkov",
    packages=setuptools.find_packages(exclude=["tests*", "integration_tests*"]),
    include_package_data=True,
    package_dir={
        "checkov.bicep.checks.graph_checks": "checkov/bicep/checks/graph_checks",
        "checkov.cloudformation.checks.graph_checks": "checkov/cloudformation/checks/graph_checks",
        "checkov.terraform.checks.graph_checks": "checkov/terraform/checks/graph_checks",
    },
    package_data={
        "checkov": ["py.typed"],
        "checkov.bicep.checks.graph_checks": ["*.yaml"],
        "checkov.common.util.templates": ["*.jinja2"],
        "checkov.terraform.checks.graph_checks": [
            "aws/*.yaml",
            "gcp/*.yaml",
            "azure/*.yaml",
        ],
    },
    scripts=["bin/checkov", "bin/checkov.cmd"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Build Tools",
        "Typing :: Typed",
    ],
)
