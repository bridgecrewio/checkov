import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.arm.checks.resource.VMCredsInCustomData import check
from checkov.arm.runner import Runner


class TestVMCredsInCustomData(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_VMCredsInCustomData"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Compute/virtualMachines.pass-no-secret",
            "Microsoft.Compute/virtualMachines.pass-no-custom-date",
            "Microsoft.Compute/virtualMachines.pass-empty-os-profile",
            "Microsoft.Compute/virtualMachines.pass-no-os-profile",
        }
        failing_resources = {
            "Microsoft.Compute/virtualMachines.fail-secret",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
