from __future__ import annotations
import pytest

from checkov.common.images.image_referencer import Image


@pytest.fixture
def file_path() -> str:
    return ".circleci/config.yml"


@pytest.fixture
def definition(file_path) -> dict:
    return {
            file_path: {
              "orbs": {
                "new-orb": "whatever/orbname@goodorb",
                "some-orb": "orbs/orbname@dev:blah",
                "__startline__": 3,
                "__endline__": 6
              },
              "executors": {
                "image-executor": {
                  "docker": [
                    {
                      "image": "mongo:2.6.8",
                      "__startline__": 9,
                      "__endline__": 11
                    }
                  ],
                  "__startline__": 8,
                  "__endline__": 11
                },
                "__startline__": 7,
                "__endline__": 11
              },
              "jobs": {
                "test-docker-hash-img": {
                  "docker": [
                    {
                      "image": "redis@sha256:54057dd7e125ca41afe526a877e8bd35ec2cdd33b9217e022ed37bdcf7d09673",
                      "__startline__": 15,
                      "__endline__": 16
                    },
                    {
                      "auth": {
                        "password": "$DOCKERHUB_PASSWORD",
                        "username": "mydockerhub-user",
                        "__startline__": 18,
                        "__endline__": 20
                      },
                      "__startline__": 17,
                      "__endline__": 20
                    }
                  ],
                  "__startline__": 13,
                  "__endline__": 20
                },
                "test-docker-latest-img": {
                  "docker": [
                    {
                      "image": "buildpack-deps:latest",
                      "__startline__": 23,
                      "__endline__": 24
                    },
                    {
                      "auth": {
                        "password": "$DOCKERHUB_PASSWORD",
                        "username": "mydockerhub-user",
                        "__startline__": 26,
                        "__endline__": 28
                      },
                      "command": [
                        "--smallfiles"
                      ],
                      "__startline__": 25,
                      "__endline__": 30
                    }
                  ],
                  "__startline__": 21,
                  "__endline__": 30
                },
                "test-docker-versioned-img": {
                  "docker": [
                    {
                      "image": "mongo:2.6.8",
                      "__startline__": 33,
                      "__endline__": 34
                    },
                    {
                      "auth": {
                        "password": "$DOCKERHUB_PASSWORD",
                        "username": "mydockerhub-user",
                        "__startline__": 36,
                        "__endline__": 38
                      },
                      "environment": {
                        "POSTGRES_USER": "user",
                        "__startline__": 39,
                        "__endline__": 40
                      },
                      "image": "postgres:14.2",
                      "__startline__": 35,
                      "__endline__": 41
                    }
                  ],
                  "__startline__": 31,
                  "__endline__": 41
                },
                "test-echo": {
                  "docker": [
                    {
                      "image": "cimg/python:latest",
                      "__startline__": 44,
                      "__endline__": 45
                    }
                  ],
                  "steps": [
                    "checkout",
                    {
                      "run": "echo \"this is an echo in a script.\"",
                      "__startline__": 48,
                      "__endline__": 49
                    }
                  ],
                  "__startline__": 42,
                  "__endline__": 49
                },
                "test-inject": {
                  "docker": [
                    {
                      "image": "cimg/python:latest",
                      "__startline__": 52,
                      "__endline__": 53
                    }
                  ],
                  "steps": [
                    "checkout",
                    {
                      "run": {
                        "command": "curl -sSJL https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -\necho ${CIRCLE_BRANCH}\n",
                        "name": "Multi-line run with injection via vars",
                        "__startline__": 56,
                        "__endline__": 60
                      },
                      "__startline__": 55,
                      "__endline__": 60
                    }
                  ],
                  "__startline__": 50,
                  "__endline__": 60
                },
                "test-inject2": {
                  "docker": [
                    {
                      "image": "cimg/python:latest",
                      "__startline__": 63,
                      "__endline__": 64
                    }
                  ],
                  "steps": [
                    "checkout",
                    {
                      "run": {
                        "command": "curl -sSJL https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -\necho $CIRCLE_BRANCH\n",
                        "name": "Multi-line run with injection via vars",
                        "__startline__": 68,
                        "__endline__": 72
                      },
                      "__startline__": 67,
                      "__endline__": 72
                    }
                  ],
                  "__startline__": 61,
                  "__endline__": 72
                },
                "test-curl-secret": {
                  "docker": [
                    {
                      "image": "cimg/python:latest",
                      "__startline__": 75,
                      "__endline__": 76
                    }
                  ],
                  "steps": [
                    "checkout",
                    {
                      "run": {
                        "command": "curl -x POST someurl $SECRET\n",
                        "name": "Multi-line export secret",
                        "__startline__": 79,
                        "__endline__": 82
                      },
                      "__startline__": 78,
                      "__endline__": 82
                    }
                  ],
                  "__startline__": 73,
                  "__endline__": 82
                },
                "test-inject-ci-vars": {
                  "docker": [
                    {
                      "image": "cimg/python:latest",
                      "__startline__": 85,
                      "__endline__": 86
                    }
                  ],
                  "steps": [
                    "checkout",
                    {
                      "run": {
                        "command": "echo ${CIRCLE_PR_REPONAME}\n",
                        "name": "Echo the PR Reponame",
                        "__startline__": 90,
                        "__endline__": 94
                      },
                      "__startline__": 89,
                      "__endline__": 94
                    }
                  ],
                  "__startline__": 83,
                  "__endline__": 94
                },
                "__startline__": 12,
                "__endline__": 94
              },
              "version": 2.1,
              "workflows": {
                "say-hello-workflow": {
                  "jobs": [
                    "test-docker-hash-img",
                    "test-docker-latest-img",
                    "test-docker-versioned-img",
                    "test-echo",
                    "test-inject",
                    "test-inject2",
                    "test-inject-ci-vars"
                  ],
                  "__startline__": 97,
                  "__endline__": 105
                },
                "__startline__": 96,
                "__endline__": 105
              },
              "__startline__": 2,
              "__endline__": 105
            }
          }