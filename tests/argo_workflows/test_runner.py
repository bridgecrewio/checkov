from pathlib import Path

from pytest_mock import MockerFixture

from checkov.argo_workflows.runner import Runner
from checkov.common.images.image_referencer import Image
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_runner_passing_check():
    # given
    test_file = EXAMPLES_DIR / "hello_world.yaml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_ARGO_2"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_failing_check():
    # given
    test_file = EXAMPLES_DIR / "hello_world.yaml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_ARGO_1"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_get_image():
    # given
    test_file = EXAMPLES_DIR / "scripts_python.yaml"

    # when
    images = Runner().get_images(str(test_file))

    # then
    assert images == {
        Image(
            file_path=str(test_file),
            name="alpine:latest",
            image_id="",
            start_line=33,
            end_line=36,
        ),
        Image(
            file_path=str(test_file),
            name="python:alpine3.6",
            image_id="",
            start_line=22,
            end_line=28,
        ),
    }

