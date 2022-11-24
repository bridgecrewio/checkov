import pytest

from checkov.circleci_pipelines.image_referencer.provider import CircleCIProvider
from checkov.circleci_pipelines.runner import Runner


def test_extract_images_from_workflow(circle_ci_filepath_workflow_with_images_config,
                                      circle_ci_image1, circle_ci_image2):
    file_path, config = circle_ci_filepath_workflow_with_images_config

    provider = CircleCIProvider(file_path=file_path, workflow_config=config)
    images = provider.extract_images_from_workflow()

    assert set(images) == {circle_ci_image1, circle_ci_image2}


def test_extract_images_from_workflow_no_images(circle_ci_filepath_workflow_no_images_config):
    file_path, config = circle_ci_filepath_workflow_no_images_config

    provider = CircleCIProvider(file_path=file_path, workflow_config=config)
    images = provider.extract_images_from_workflow()

    assert not images

@pytest.mark.parametrize(
    "start_line, end_line, tag, supported_entities, old_key_format, expected_key",
    [
        (21,
         22,
         'jobs',
        ('jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}',),
         'jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}.jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}.CKV_CIRCLECIPIPELINES_1[85:86]',
         "jobs(test-docker-versioned-img).docker.image[1](mongo:2.6.8)"),
    ],
)
def test_generate_resource_key_generates_same_key_as_get_resource(file_path,
                                                                  start_line, end_line, tag,
                                                                  supported_entities,
                                                                  old_key_format, expected_key,
                                                                  circleci_config_with_images_definitions):
    definitions = circleci_config_with_images_definitions.get(file_path)
    provider = CircleCIProvider(definitions, file_path)
    runner = Runner()
    runner.definitions[file_path] = definitions

    key1 = runner.get_resource(file_path, old_key_format, supported_entities, start_line, end_line)
    key2 = provider.generate_resource_key(start_line, end_line, tag)

    assert key1 == key2 == expected_key
