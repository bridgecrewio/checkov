import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.oci.SecurityListUnrestrictedIngress22 import check
from checkov.terraform.runner import Runner


class TestSecurityListUnrestrictedIngress22(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SecurityListUnrestrictedIngress22"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        expected_passing_resources = {
            "oci_core_security_list.pass0",
            "oci_core_security_list.pass1",
            "oci_core_security_list.pass4",
            "oci_core_security_list.pass5",
            "oci_core_security_list.pass6",
        }
        expected_failing_resources = {
            "oci_core_security_list.fail",
            "oci_core_security_list.fail1",
            "oci_core_security_list.fail2",
            "oci_core_security_list.fail3",
            "oci_core_security_list.fail5",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], len(expected_passing_resources))
        self.assertEqual(summary["failed"], len(expected_failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(expected_passing_resources, passed_check_resources)
        self.assertEqual(expected_failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
