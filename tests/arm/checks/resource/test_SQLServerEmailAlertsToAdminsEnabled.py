import os
import unittest
from pathlib import Path

from checkov.arm.checks.resource.SQLServerEmailAlertsToAdminsEnabled import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestSQLServerEmailAlertsToAdminsEnabled(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SQLServerEmailAlertsToAdminsEnabled"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_email_account_admins_values(self):
        # given
        test_file = Path(__file__).parent / "example_SQLServerEmailAlertsToAdminsEnabled/emailAccountAdmins.json"

        # when
        report = Runner().run(root_folder=None, files=[str(test_file)], runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Sql/servers/databases.sqlserver/admins-enabled",
            "Microsoft.Sql/servers/databases.sqlserver/admins-true",
            # the value is only known at deployment time
            "Microsoft.Sql/servers/databases.sqlserver/admins-parameter",
        }
        failing_resources = {
            "Microsoft.Sql/servers/databases.sqlserver/admins-disabled",
            "Microsoft.Sql/servers/databases.sqlserver/admins-false",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
