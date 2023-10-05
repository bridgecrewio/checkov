import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.github.SecretsEncrypted import check
from checkov.terraform.runner import Runner


class TestSecretsEncrypted(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_SecretsEncrypted"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "github_actions_environment_secret.pass",
            "github_actions_organization_secret.pass",
            "github_actions_organization_secret.pass_empty_value",
            "github_actions_secret.pass",
        }
        failing_resources = {
            "github_actions_environment_secret.fail",
            "github_actions_organization_secret.fail",
            "github_actions_secret.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        # github_actions_secret.value_ref is dependent on azuread_service_principal_password.gh_actions
        self.assertEqual(summary["resource_count"], 9)  # 2 extra

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
