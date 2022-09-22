from checkov.common.images.image_referencer import Image
from checkov.gitlab_ci.image_referencer.base_provider import GitlabCiProvider


def test_extract_images_from_workflow():
    file_path = 'tests/gitlab_ci/resources/images/.gitlab-ci.yml'
    workflow_config = {
              "default": {
                "image": "nginx:1.18",
                "services": [
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
              "__startline__": 1,
              "__endline__": 32
            }

    gitlab_ci_provider = GitlabCiProvider(workflow_config=workflow_config, file_path=file_path)
    images = gitlab_ci_provider.extract_images_from_workflow()

    assert images == [
        Image(
            end_line=17,
            start_line=2,
            file_path=file_path,
            name='nginx:1.18',
            related_resource_id=None
        ),
        Image(
            end_line=12,
            start_line=11,
            file_path=file_path,
            name='redis:latest',
            related_resource_id=None
        ),
        Image(
            end_line=12,
            start_line=11,
            file_path=file_path,
            name='nginx:1.17',
            related_resource_id=None
        )
    ]


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
