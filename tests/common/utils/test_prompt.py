from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import click
import pytest
from _pytest.capture import CaptureFixture
from checkov.common.util import prompt


@pytest.fixture(autouse=True)
def checkov_root_mock(tmp_path: Path):
    with mock.patch("checkov.common.util.prompt.CHECKOV_ROOT_DIRECTORY", str(tmp_path / "checkov")):
        yield


def test_prompt_terraform_aws_resource(capsys: CaptureFixture[str]):
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

    expected = [
        f"Creating Check {test_name}.py",
        f"Creating Unit Test Stubs for {test_name}",
        "Successfully created",
        f"checkov/terraform/checks/resource/aws/{test_name}.py",
        "Next steps:",
    ]

    for exp in expected:
        assert exp in captured.out


def test_prompt_terraform_azure_resource(capsys: CaptureFixture[str]):
    test_name = "AzureTestPromptUnitTest"
    choices = [
        "add",
        f"{test_name}",
        "iam",
        "Tests for the Azure Prompt Unit Test",
        "terraform",
        "azure",
        "resource",
        "azurerm_policy_definition",
    ]

    mock_click = click
    mock_click.prompt = MagicMock(name="prompt", side_effect=choices)
    resp = prompt.Prompt()
    check = prompt.Check(resp.responses)
    check.action()

    captured = capsys.readouterr()

    expected = [
        f"Creating Check {test_name}.py",
        f"Creating Unit Test Stubs for {test_name}",
        "Successfully created",
        f"checkov/terraform/checks/resource/azure/{test_name}.py",
        "Next steps:",
    ]

    for exp in expected:
        assert exp in captured.out


def test_prompt_terraform_gcp_resource(capsys: CaptureFixture[str]):
    test_name = "GCPTestPromptUnitTest"
    choices = [
        "add",
        f"{test_name}",
        "iam",
        "Tests for the GCP Prompt Unit Test",
        "terraform",
        "gcp",
        "resource",
        "google_project_iam_policy",
    ]

    mock_click = click
    mock_click.prompt = MagicMock(name="prompt", side_effect=choices)
    resp = prompt.Prompt()
    check = prompt.Check(resp.responses)
    check.action()

    captured = capsys.readouterr()

    expected = [
        f"Creating Check {test_name}.py",
        f"Creating Unit Test Stubs for {test_name}",
        "Successfully created",
        f"checkov/terraform/checks/resource/gcp/{test_name}.py",
        "Next steps:",
    ]

    for exp in expected:
        assert exp in captured.out
