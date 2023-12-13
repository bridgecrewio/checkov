#!/usr/bin/env python
import json
import logging
import os
from importlib import util
from os import path
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py


class PreBuildCommand(build_py):
    """Pre-build command"""

    def transform_graph_yaml_to_json(self) -> None:
        """Transforms YAML graph checks to JSON and copies them to build/lib"""

        import yaml  # can't be top-level, because it needs to be first installed via 'setup_requires'

        graph_check_paths = ("checkov/*/checks/graph_checks",)
        build_path = Path(self.build_lib)
        src_path = Path()

        for graph_check_path in graph_check_paths:
            for yaml_file in src_path.glob(f"{graph_check_path}/**/*.yaml"):
                json_file = (build_path / yaml_file).with_suffix(".json")
                self.mkpath(str(json_file.parent))
                json_file.write_text(json.dumps(yaml.safe_load(yaml_file.read_text())))

    def run(self) -> None:
        self.execute(self.transform_graph_yaml_to_json, ())
        build_py.run(self)


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
    cmdclass={
        "build_py": PreBuildCommand,
    },
    setup_requires=[
        "pyyaml",
    ],
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
        "bc-python-hcl2==0.4.2",
        "bc-detect-secrets==1.4.30",
        "bc-jsonpath-ng==1.6.1",
        "tabulate",
        "colorama",
        "termcolor",
        "junit-xml>=1.9",
        "dpath==2.1.3",
        "pyyaml>=5.4.1",
        "boto3>=1.17",
        "gitpython",
        "jmespath",
        "tqdm",
        "update-checker",
        "semantic-version",
        "packaging",
        "cloudsplaining>=0.6.2",
        "networkx<2.7",
        "igraph<0.11.0",
        "dockerfile-parse",
        "docker",
        "configargparse",
        "argcomplete",
        "typing-extensions>=4.1.0",
        "importlib-metadata>=0.12",
        "cachetools",
        "cyclonedx-python-lib==5.2.0",
        "packageurl-python",
        "click>=8.0.0",
        "aiohttp",
        "aiodns",
        "aiomultiprocess",
        "jsonschema>=4.6.0,<5.0.0",
        "prettytable>=3.0.0",
        "pycep-parser==0.4.1",
        "charset-normalizer",
        "pyston-autoload==2.3.5; python_version < '3.11' and (sys_platform == 'linux' or sys_platform == 'darwin') and platform_machine == 'x86_64' and implementation_name == 'cpython'",
        "pyston==2.3.5; python_version < '3.11' and (sys_platform == 'linux' or sys_platform == 'darwin') and platform_machine == 'x86_64' and implementation_name == 'cpython'",
        "schema",
        "requests>=2.27.0",
        "yarl",
        "openai<1.0.0",
        "spdx-tools<0.9.0,>=0.8.0",
        "license-expression",
        "rustworkx",
        "pydantic",
    ],
    dependency_links=[],  # keep it empty, needed for pipenv-setup
    license="Apache License 2.0",
    name="checkov",
    version=version,
    python_requires=">=3.8",
    description="Infrastructure as code static analysis",
    author="bridgecrew",
    author_email="meet@bridgecrew.io",
    url="https://github.com/bridgecrewio/checkov",
    packages=find_packages(
        exclude=[
            "dogfood_tests*",
            "flake8_plugins*",
            "integration_tests*",
            "performance_tests*",
            "tests*",
        ]
    ),
    include_package_data=True,
    package_data={
        "checkov": ["py.typed"],
        "checkov.common.util.templates": ["*.jinja2"],
        "checkov.ansible.checks.graph_checks": ["**/*.json"],
        "checkov.arm.checks.graph_checks": ["**/*.json"],
        "checkov.bicep.checks.graph_checks": ["**/*.json"],
        "checkov.cloudformation.checks.graph_checks": ["**/*.json"],
        "checkov.dockerfile.checks.graph_checks": ["**/*.json"],
        "checkov.github_actions.checks.graph_checks": ["**/*.json"],
        "checkov.kubernetes.checks.graph_checks": ["**/*.json"],
        "checkov.terraform.checks.graph_checks": ["**/*.json"],
        "checkov.sast.checks": [
            "java/*.yaml",
            "python/*.yaml",
            "javascript/*.yaml",
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Build Tools",
        "Typing :: Typed",
    ],
)
