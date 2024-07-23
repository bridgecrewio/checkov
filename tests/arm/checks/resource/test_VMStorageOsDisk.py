import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.arm.checks.resource.VMStorageOsDisk import check
from checkov.arm.runner import Runner


class TestVMStorageOsDisk(unittest.TestCase):

    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_VMStorageOsDisk"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Compute/virtualMachines.pass-linux",
            "Microsoft.Compute/virtualMachines.pass-windows",
        }
        failing_resources = {
            "Microsoft.Compute/virtualMachines.fail-linux",
            "Microsoft.Compute/virtualMachines.fail-windows",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 4)  # 3 unknown

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
