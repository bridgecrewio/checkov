import os
import unittest
import click
import sys
import pytest
import shutil
import glob


from unittest import mock
from unittest.mock import MagicMock
from checkov.common.models.consts import SCAN_HCL_FLAG
from checkov.common.util.config_utils import should_scan_hcl_files
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util import prompt
from click.testing import CliRunner


class TestPrompt(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def set_up(self):
        # nothing
        print("Setting up")

        # Important! In order to make cleanup easy (and automatic), all created files and directories should
        # contain the TestPromptUnitTest string. We'll pattern match on that to remove them after every test!
    def tearDown(self):
        base = os.path.abspath(os.path.join("."))
        for file_or_dir in glob.glob(f"{base}/**/*TestPromptUnitTest*", recursive=True):
            if not os.path.exists(file_or_dir):
                continue  # Skip if doesn't exist (probably already removed)

            if os.path.isfile(file_or_dir) or os.path.islink(file_or_dir):
                os.remove(file_or_dir)
            elif os.path.isdir(file_or_dir):
                shutil.rmtree(file_or_dir)

    def test_prompt_terraform_aws_resource(self):
        test_name = "AWSTestPromptUnitTest"
        choices = ["add", f"{test_name}", "iam", "Tests for the AWS Prompt Unit Test",
                   "terraform", "aws", "resource", "aws_iam_policy"]

        mock_click = click
        mock_click.prompt = MagicMock(name="prompt", side_effect=choices)
        resp = prompt.Prompt()
        check = prompt.Check(resp.responses)
        check.action()

        captured = self.capsys.readouterr()

        expected = [
            f"Creating Check {test_name}.py",
            f"Creating Unit Test Stubs for {test_name}",
            "Successfully created",
            f"checkov/terraform/checks/resource/aws/{test_name}.py",
            "Next steps:"
        ]

        for exp in expected:
            self.assertTrue(exp in captured.out)

    def test_prompt_terraform_azure_resource(self):
        test_name = "AzureTestPromptUnitTest"
        choices = ["add", f"{test_name}", "iam", "Tests for the Azure Prompt Unit Test",
                   "terraform", "azure", "resource", "azurerm_policy_definition"]

        mock_click = click
        mock_click.prompt = MagicMock(name="prompt", side_effect=choices)
        resp = prompt.Prompt()
        check = prompt.Check(resp.responses)
        check.action()

        captured = self.capsys.readouterr()

        expected = [
            f"Creating Check {test_name}.py",
            f"Creating Unit Test Stubs for {test_name}",
            "Successfully created",
            f"checkov/terraform/checks/resource/azure/{test_name}.py",
            "Next steps:"
        ]

        for exp in expected:
            self.assertTrue(exp in captured.out)

    def test_prompt_terraform_gcp_resource(self):
        test_name = "GCPTestPromptUnitTest"
        choices = ["add", f"{test_name}", "iam", "Tests for the GCP Prompt Unit Test",
                   "terraform", "gcp", "resource", "google_project_iam_policy"]

        mock_click = click
        mock_click.prompt = MagicMock(name="prompt", side_effect=choices)
        resp = prompt.Prompt()
        check = prompt.Check(resp.responses)
        check.action()

        captured = self.capsys.readouterr()

        expected = [
            f"Creating Check {test_name}.py",
            f"Creating Unit Test Stubs for {test_name}",
            "Successfully created",
            f"checkov/terraform/checks/resource/gcp/{test_name}.py",
            "Next steps:"
        ]

        for exp in expected:
            self.assertTrue(exp in captured.out)


if __name__ == '__main__':
    unittest.main()
