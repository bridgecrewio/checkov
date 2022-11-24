from checkov.common.images.image_referencer import Image
from checkov.github_actions.image_referencer.manager import GithubActionsImageReferencerManager


def test_extract_images_from_workflow(workflow_with_images, workflow_line_numbers_with_image):
    file_path = '/.github/workflows/workflow_with_string_container.yml'

    manager = GithubActionsImageReferencerManager(file_path=file_path, workflow_config=workflow_with_images,
                                                  workflow_line_numbers=workflow_line_numbers_with_image)
    images = manager.extract_images_from_workflow()

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

    manager = GithubActionsImageReferencerManager(file_path=file_path, workflow_config=workflow_without_images,
                                                  workflow_line_numbers=workflow_line_numbers_without_image)
    images = manager.extract_images_from_workflow()

    assert not images
