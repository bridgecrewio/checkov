from checkov.circleci_pipelines.image_referencer.manager import CircleCIImageReferencerManager


def test_extract_images_from_workflow(circle_ci_filepath_workflow_with_images_config,
                                      circle_ci_image1, circle_ci_image2):
    file_path, config = circle_ci_filepath_workflow_with_images_config

    manager = CircleCIImageReferencerManager(file_path=file_path, workflow_config=config)
    images = manager.extract_images_from_workflow()

    assert set(images) == {circle_ci_image1, circle_ci_image2}


def test_extract_images_from_workflow_no_images(circle_ci_filepath_workflow_no_images_config):
    file_path, config = circle_ci_filepath_workflow_no_images_config

    manager = CircleCIImageReferencerManager(file_path=file_path, workflow_config=config)
    images = manager.extract_images_from_workflow()

    assert not images

def test_extract_images_from_workflow_nested(circle_ci_filepath_workflow_no_images_config):
    file_path = '/tmp/test_path'
    config = {
        'workspace_root': '/go/src/github.com/gruntwork-io/terragrunt',
        'defaults': {
            'working_directory': '/go/src/github.com/gruntwork-io/terragrunt', 'docker': [
                {'image': '087285199408.dkr.ecr.us-east-1.amazonaws.com/circle-ci-test-image-base:go1.11',
                    '__startline__': 6, '__endline__': 8}], '__startline__': 3, '__endline__': 8
        },
        'jobs': {
            'install_dependencies': {
                'working_directory': '/go/src/github.com/gruntwork-io/terragrunt', 'docker': [
                {'image': '087285199408.dkr.ecr.us-east-1.amazonaws.com/circle-ci-test-image-base:go1.11',
                 '__startline__': 6, '__endline__': 8}], 'steps': ['checkout'], '__startline__': 11, '__endline__': 32
            }
        }, '__startline__': 1, '__endline__': 143
    }

    manager = CircleCIImageReferencerManager(file_path=file_path, workflow_config=config)
    images = manager.extract_images_from_workflow()

    assert not images
