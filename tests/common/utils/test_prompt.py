import os
from unittest.mock import MagicMock
import click
from _pytest.capture import CaptureFixture
from checkov.common.util import prompt


repo_root = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)
resource_tests_directory = os.path.join(repo_root, "tests", "terraform", "checks", "resource")
resource_check_directory = os.path.join(repo_root, "checkov", "terraform", "checks", "resource")


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

    # Remove unit test files
    os.remove(os.path.join(resource_tests_directory, "aws", f"test_{test_name}.py"))
    os.remove(os.path.join(resource_tests_directory, "aws", f"example_{test_name}/{test_name}.tf"))
    os.removedirs(os.path.join(resource_tests_directory, "aws", f"example_{test_name}"))
    # Remove check files
    os.remove(os.path.join(resource_check_directory, "aws", f"{test_name}.py"))


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
    # Remove unit test files
    os.remove(os.path.join(resource_tests_directory, "azure", f"test_{test_name}.py"))
    os.remove(os.path.join(resource_tests_directory, "azure", f"example_{test_name}/{test_name}.tf"))
    os.removedirs(os.path.join(resource_tests_directory, "azure", f"example_{test_name}"))
    # Remove check files
    os.remove(os.path.join(resource_check_directory, "azure", f"{test_name}.py"))


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
    # Remove unit test files
    os.remove(os.path.join(resource_tests_directory, "gcp", f"test_{test_name}.py"))
    os.remove(os.path.join(resource_tests_directory, "gcp", f"example_{test_name}/{test_name}.tf"))
    os.removedirs(os.path.join(resource_tests_directory, "gcp", f"example_{test_name}"))
    # Remove check files
    os.remove(os.path.join(resource_check_directory, "gcp", f"{test_name}.py"))
