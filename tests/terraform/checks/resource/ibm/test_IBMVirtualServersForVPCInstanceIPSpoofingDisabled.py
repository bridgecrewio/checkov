import logging
import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.ibm.IBMVirtualServersForVPCInstanceIPSpoofingDisabled import check


class IBMVirtualServersForVPCInstanceIPSpoofingDisabled(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_IBMVirtualServersForVPCInstanceIPSpoofingDisabled")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "ibm_is_instance.pass_1",
            "ibm_is_instance.pass_2",
        }
        failing_resources = {
            "ibm_is_instance.fail_1",
            "ibm_is_instance.fail_2",
            "ibm_is_instance.fail_3"
        }
        skipped_resources = {}

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], len(skipped_resources))
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()