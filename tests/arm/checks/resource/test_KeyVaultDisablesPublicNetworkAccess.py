import unittest
from pathlib import Path
from checkov.arm.checks.resource.KeyVaultDisablesPublicNetworkAccess import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestKeyVaultDisablesPublicNetworkAccess(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_KeyVaultDisablesPublicNetworkAccess"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()
        print(f'\n{summary}')

        passing_resources = {
            "Microsoft.KeyVault/vaults.pass1",
            "Microsoft.KeyVault/vaults.pass2",
            "Microsoft.KeyVault/vaults.pass3",
            "Microsoft.KeyVault/vaults.pass4",
        }
        failing_resources = {
            "Microsoft.KeyVault/vaults.fail1",
            "Microsoft.KeyVault/vaults.fail2",
            "Microsoft.KeyVault/vaults.fail3",
            "Microsoft.KeyVault/vaults.fail4",
            "Microsoft.KeyVault/vaults.fail5",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()