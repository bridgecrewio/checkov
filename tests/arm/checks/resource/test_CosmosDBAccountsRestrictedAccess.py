import os
import unittest

from checkov.arm.checks.resource.CosmosDBAccountsRestrictedAccess import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCosmosDBAccountsRestrictedAccess(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_CosmosDBAccountsRestrictedAccess"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.DocumentDB/databaseAccounts.pass",
            "Microsoft.DocumentDB/databaseAccounts.pass2",
            "Microsoft.DocumentDB/databaseAccounts.pass3",
            "Microsoft.DocumentDB/databaseAccounts.pass4",
        }
        failing_resources = {
            "Microsoft.DocumentDB/databaseAccounts.fail",
            "Microsoft.DocumentDB/databaseAccounts.fail2",
            "Microsoft.DocumentDB/databaseAccounts.fail3",
            "Microsoft.DocumentDB/databaseAccounts.fail4",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 4)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
