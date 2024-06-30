import unittest
from pathlib import Path
from checkov.arm.checks.resource.MariaDBGeoBackupEnabled import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestMariaDBGeoBackupEnabled(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_MariaDBGeoBackupEnabled"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        passing_resources = {
            "Microsoft.DBforMariaDB/servers.pass",
        }
        failing_resources = {
            "Microsoft.DBforMariaDB/servers.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(passed_check_resources,passing_resources)
        self.assertEqual(failed_check_resources,failing_resources)


if __name__ == '__main__':
    unittest.main()
