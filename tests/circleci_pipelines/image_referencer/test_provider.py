

from checkov.circleci_pipelines.image_referencer.provider import CircleCIProvider


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
