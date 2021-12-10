import os
import shutil
from unittest.mock import MagicMock
import click
from _pytest.capture import CaptureFixture


def test_generated_rules_custom_directories(capsys: CaptureFixture[str]):
    checkov_pkg_dir_mock = os.path.join(os.path.dirname(__file__), "tmp")
    checkov_test_dir_mock = os.path.join(os.path.dirname(__file__), "tmp_tests")
    os.makedirs(checkov_pkg_dir_mock, exist_ok=True)
    os.makedirs(checkov_test_dir_mock, exist_ok=True)
    os.environ["CKV_PKG_DIRECTORY"] = checkov_pkg_dir_mock
    os.environ["CKV_TEST_DIRECTORY"] = checkov_test_dir_mock
    # Need to re-import the module to get the environment variable to work
    from checkov.common.util import prompt

    test_name = "AWSTestPromptUnitTest"
    choices = [
        "add",
        f"{test_name}",
        "iam",
        "Tests for the AWS Prompt Unit Test",
        "terraform",
        "aws",
        "resource",
        "aws_iam_policy",
    ]

    mock_click = click
    mock_click.prompt = MagicMock(name="prompt", side_effect=choices)
    resp = prompt.Prompt()
    check = prompt.Check(resp.responses)
    check.action()

    captured = capsys.readouterr()
    print(captured.out)
    target_test_dir = os.path.join(checkov_test_dir_mock, "terraform", "checks", "resource", "aws")
    assert(os.path.exists(os.path.join(target_test_dir, f"test_{test_name}.py")))
    assert(os.path.exists(os.path.join(target_test_dir, f"example_{test_name}", f"{test_name}.tf")))
    shutil.rmtree(checkov_pkg_dir_mock)
    shutil.rmtree(checkov_test_dir_mock)

