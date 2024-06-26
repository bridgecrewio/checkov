import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.arm.runner import Runner
from checkov.arm.checks.resource.AKSEphemeralOSDisks import check


class TestAKSEphemeralOSDisks(unittest.TestCase):

    def test(self):
        test_files_dir = Path(__file__).parent / "example_AKSEphemeralOSDisks"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        summary = report.get_summary()

        passing_resources = {
            'Microsoft.ContainerService.pass',
        }
        failing_resources = {
            'Microsoft.ContainerService.fail',
            'Microsoft.ContainerService.fail2',
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
