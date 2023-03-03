from __future__ import annotations
from typing import Any, Tuple

import pytest


@pytest.fixture
def supported_entities() -> Tuple[str, str]:
    return 'jobs', 'stages[].jobs[]'


@pytest.fixture
def definitions() -> dict[str, Any]:
    return {
        '/checkov/tests/azure_pipelines/resources/azure-pipelines.yml': {
            'trigger': ['master'],
            'resources': {
                'repositories': [
                    {
                        'repository': 'AzureDevOps',
                        'type': 'git',
                        'endpoint': 'AzureDevOps',
                        'name': 'AzureDevOps/AzureDevOps',
                        '__startline__': 6,
                        '__endline__': 11
                    }
                ],
                '__startline__': 5,
                '__endline__': 11
            },
            'stages': [
                {
                    'stage': 'Example',
                    'jobs': [
                        {
                            'job': 'FailNoTag',
                            'displayName': 'FailNoTagDisplayName',
                            'pool': {
                                'vmImage': 'ubuntu-18.04',
                                '__startline__': 16,
                                '__endline__': 18
                            },
                            'container': 'ubuntu',
                            'steps': [
                                {
                                    'script': 'printenv',
                                    '__startline__': 21,
                                    '__endline__': 22
                                }
                            ],
                            '__startline__': 14,
                            '__endline__': 22
                        },
                        {
                            'job': 'PassDigest',
                            'pool': {
                                'vmImage': 'ubuntu-18.04',
                                '__startline__': 24,
                                '__endline__': 26
                            },
                            'container': 'ubuntu@sha256:a0a45bd8c6c4acd6967396366f01f2a68f73406327285edc5b7b07cb1cf073db',
                            'steps': [
                                {
                                    'script': 'printenv',
                                    '__startline__': 29,
                                    '__endline__': 31
                                }
                            ],
                            '__startline__': 22,
                            '__endline__': 31
                        }
                    ],
                    '__startline__': 12,
                    '__endline__': 31
                }
            ],
            'jobs': [
                {
                    'job': 'FailTag',
                    'pool': {
                        'vmImage': 'ubuntu-18.04',
                        '__startline__': 34,
                        '__endline__': 36
                    },
                    'container': 'ubuntu:20.04',
                    'steps': [
                        {
                            'script': 'printenv',
                            '__startline__': 39,
                            '__endline__': 39
                        }
                    ],
                    '__startline__': 32,
                    '__endline__': 39
                }
            ],
            '__startline__': 1,
            '__endline__': 39
        }
    }
