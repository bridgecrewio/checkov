import pytest

from checkov.common.images.image_referencer import Image
from checkov.github_actions.image_referencer.provider import GithubActionProvider
from checkov.github_actions.runner import Runner

def test_extract_images_from_workflow(workflow_with_images, workflow_line_numbers_with_image):
    file_path = '/.github/workflows/workflow_with_string_container.yml'

    gha_provider = GithubActionProvider(file_path=file_path, workflow_config=workflow_with_images,
                                        workflow_line_numbers=workflow_line_numbers_with_image)
    images = gha_provider.extract_images_from_workflow()

    assert images == [
        Image(
            end_line=13,
            start_line=12,
            name='node:14.16',
            file_path=file_path,
            related_resource_id='jobs(destroy_cert)'
        )
    ]


def test_extract_images_from_workflow_no_images(workflow_without_images, workflow_line_numbers_without_image):
    file_path = '/.github/workflows/unsecure_command.yaml'

    gha_provider = GithubActionProvider(file_path=file_path, workflow_config=workflow_without_images,
                                        workflow_line_numbers=workflow_line_numbers_without_image)
    images = gha_provider.extract_images_from_workflow()

    assert not images


@pytest.mark.parametrize(
    "start_line,end_line,expected_key",
    [
        (9, 17, "jobs(container-test-job)"),
        (24, 30, "jobs(second_job)"),
        (35, 40, "")
    ],
)
def test_generate_resource_key(start_line, end_line, expected_key, definition):
    gha_provider = GithubActionProvider(definition, '', [])

    key = gha_provider.generate_resource_key(start_line, end_line)

    assert key == expected_key


@pytest.mark.parametrize(
    "start_line, end_line, supported_entities, old_key_format, expected_key",
    [
        (9, 17, ('jobs', 'jobs.*.steps[]'), 'jobs.container-test-job.CKV_GHA_3[7:23]', "jobs(container-test-job)"),
        (24, 30, ('jobs', 'jobs.*.steps[]'), "jobs.second_job.CKV_GHA_3[24:30]", "jobs(second_job)")
    ],
)
def test_generate_resource_key_generates_same_key_as_get_resource(start_line, end_line, supported_entities,
                                                                  old_key_format, expected_key, definition):
    gha_provider = GithubActionProvider(definition, '', [])
    runner = Runner()
    file_path = "mock_path"
    runner.definitions[file_path] = definition

    key1 = runner.get_resource(file_path, old_key_format, supported_entities, start_line, end_line)
    key2 = gha_provider.generate_resource_key(start_line, end_line)

    assert key1 == key2 == expected_key
