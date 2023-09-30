from checkov.common.images.image_referencer import Image
from checkov.gitlab_ci.image_referencer.provider import GitlabCiProvider


def test_extract_images_from_workflow():
    file_path = 'tests/gitlab_ci/resources/images/.gitlab-ci.yml'
    workflow_config = {
        "default": {
            "image": {
                "name": "ruby:2.6",
                "entrypoint": [
                    "/bin/bash"
                ],
                "__startline__": 3,
                "__endline__": 6
            },
            "services": [
                {
                    "name": "privateregistry/stuff/my-postgres:11.7",
                    "alias": "db-postgres",
                    "__startline__": 7,
                    "__endline__": 9
                },
                {
                    "name": "redis:latest",
                    "__startline__": 9,
                    "__endline__": 10
                },
                "nginx:1.17"
            ],
            "before_script": [
                "bundle install"
            ],
            "__startline__": 2,
            "__endline__": 15
        },
        "__startline__": 1,
        "__endline__": 32
    }

    gitlab_ci_provider = GitlabCiProvider(workflow_config=workflow_config, file_path=file_path)
    images = gitlab_ci_provider.extract_images_from_workflow()

    assert set(images) == {
        Image(
            end_line=6,
            start_line=3,
            file_path=file_path,
            name='ruby:2.6',
            related_resource_id='default.image'
        ),
        Image(
            end_line=10,
            start_line=9,
            file_path=file_path,
            name='redis:latest',
            related_resource_id='default.services.2'
        ),
        Image(
            end_line=10,
            start_line=9,
            file_path=file_path,
            name='nginx:1.17',
            related_resource_id='default.services.2'
        ),
        Image(
            end_line=9,
            start_line=7,
            file_path=file_path,
            name='privateregistry/stuff/my-postgres:11.7',
            related_resource_id='default.services.1'
        )
    }


def test_extract_images_from_workflow_no_images():
    file_path = 'tests/gitlab_ci/resources/rules/.gitlab-ci.yml'
    workflow_config = {
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
    }

    gitlab_ci_provider = GitlabCiProvider(workflow_config=workflow_config, file_path=file_path)
    images = gitlab_ci_provider.extract_images_from_workflow()

    assert not images


def test_extract_images_from_workflow_image_without_name():
    file_path = 'tests/gitlab_ci/resources/rules/image_without_name.gitlab-ci.yml'
    workflow_config = {
          "unit tests": {
            "image": {
              "entrypoint": [
                "/opt/bin/entry_point_unit_tests.sh"
              ],
              "__startline__": 3,
              "__endline__": 6
            },
            "services": [
              {
                "name": "postgres:13.2",
                "alias": "postgres",
                "__startline__": 7,
                "__endline__": 8
              }
            ],
            "__startline__": 2,
            "__endline__": 8
          },
          "__startline__": 1,
          "__endline__": 8
        }

    gitlab_ci_provider = GitlabCiProvider(workflow_config=workflow_config, file_path=file_path)
    images = gitlab_ci_provider.extract_images_from_workflow()

    assert len(images) == 1
    assert images[0] == Image(name='postgres:13.2', file_path=file_path, start_line=7, end_line=8, related_resource_id='unit tests.services.1')
