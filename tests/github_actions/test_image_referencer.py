from pathlib import Path

RESOURCE_DIR = Path(__file__).parent / "resources/.github/workflows"
from checkov.github_actions.runner import Runner


def test_get_images_dict_container():
    runner = Runner()

    images = list(runner.get_images(str(RESOURCE_DIR) + "/workflow_with_image.yml"))

    assert len(images) == 1
    assert images[0].name == "node:14.16"
    assert images[0].start_line == 9
    assert images[0].end_line == 17


def test_get_images_str_container():
    runner = Runner()

    images = list(runner.get_images(str(RESOURCE_DIR) + "/workflow_with_string_container.yml"))

    assert len(images) == 1
    assert images[0].name == "node:14.16"
    assert images[0].start_line == 12
    assert images[0].end_line == 13

