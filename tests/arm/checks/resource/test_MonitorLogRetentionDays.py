import unittest
from pathlib import Path

from checkov.arm.checks.resource.MonitorLogProfileRetentionDays import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestMonitorLogProfileRetentionDays(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_MonitorLogProfileRetentionDays"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Insights/logprofiles.enabled",
        }

        failing_resources = {
            "Microsoft.Insights/logprofiles.disabled",
            "Microsoft.Insights/logprofiles.low",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertSetEqual(passing_resources, passed_check_resources)
        self.assertSetEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
