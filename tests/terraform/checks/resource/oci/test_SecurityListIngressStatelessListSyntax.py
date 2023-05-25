import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.oci.SecurityListIngressStateless import check
from checkov.terraform.runner import Runner


class TestSecurityListIngressStateless(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SecurityListIngressStatelessListSyntax"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "oci_core_security_list.pass",
            "oci_core_security_list.pass2",
            "oci_core_security_list.pass3",
            "oci_core_security_list.pass4",
        }

        failing_resources = {
            "oci_core_security_list.fail",
            "oci_core_security_list.fail2",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
