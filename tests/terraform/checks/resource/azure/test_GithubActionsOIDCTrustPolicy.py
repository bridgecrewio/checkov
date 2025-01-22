import os
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.GithubActionsOIDCTrustPolicy import check
from checkov.terraform.runner import Runner
from checkov.terraform.plan_runner import Runner as PlanRunner


class TestAzureGithubActionsOIDCTrustPolicy(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_GithubActionsOIDCTrustPolicy"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "azuread_application_federated_identity_credential.pass1",
            "azuread_application_federated_identity_credential.pass2",
            "azuread_application_federated_identity_credential.pass4",
        }
        failing_resources = {
            "azuread_application_federated_identity_credential.fail1",
            "azuread_application_federated_identity_credential.fail2",
            "azuread_application_federated_identity_credential.fail3",
            "azuread_application_federated_identity_credential.fail5",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
